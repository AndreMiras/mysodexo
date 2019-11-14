# Reverse Engineering Sodexo's API

## Abstract
This is documenting my journey to reverse engineering [Sodexo's meal pass card](https://en.wikipedia.org/wiki/Sodexo) API.
The idea is to understand and describe their API to later develop clients for it.
One way to achieve it is by decompiling the [Sodexo Android app](https://play.google.com/store/apps/details?id=com.sodexo.app) APK and look into it.
The APK in its version 2.4.4 (released the October 3rd 2019) was used.


## Motivations
1. it's fun & challenging
2. for the sake of open source
3. I'd like to be able to know my Sodexo card balance from command line before leaving for lunch
```sh
$ mysodexo
€123.45
```

## Download APK from device
To have access to the APK on our host, we can download it from the device with [`adb`](https://developer.android.com/studio/command-line/adb).
We first need to know where the APK is stored on device.
```sh
adb shell pm list packages -f | grep sodexo
```
Output:
```sh
package:/data/app/com.sodexo.app-1/base.apk=com.sodexo.app
```
For some reason we cannot download directly from the `/data/` dir to our host.
So we need to copy it over the device `/sdcard/` beforehand.
```sh
adb shell cp /data/app/com.sodexo.app-1/base.apk /sdcard/
adb pull /sdcard/base.apk .
```

## Decompile
There're various tools even online ones.
I first gave [Apktool](https://ibotpeaches.github.io/Apktool/) a try, but the result code was hard to follow so I switched to [jadx](https://github.com/skylot/jadx) (version 1.0.0) and was happy with the result.
```sh
jadx --output-dir base base.apk
```
One of the first things we do then is to send a couple of `grep` commands to find URLs in the source code.
We quickly come across the `resources/res/values/strings.xml` file that contains the following extract:
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="HOST">https://sodexows.mo2o.com/</string>
    ...
    <string name="clientCertP12">sodexows.mo2o.com_client-android.p12</string>
    <string name="clientCertP12Password">android</string>
    <string name="clientCertPEM">master-cacert.pem</string>
    ...
<resources>
```

## First try with the base URL
Since we already have what looks like our base API URL, we want to `curl` it.
```sh
curl https://sodexows.mo2o.com/
```
Response:
```
curl: (56) OpenSSL SSL_read: error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure, errno 0
```
Looking deeper with `--verbose` flag we see the server side certificate is OK as signed by GoDaddy.com, but the server is most likely checking client side certificate.
The good thing is we have access to the client certificate from the APK.

## Certs
Remember we have the `assets/sodexows.mo2o.com_client-android.p12` file which seems like a client certificate in [PKCS 12](https://en.wikipedia.org/wiki/PKCS_12) format.
```sh
curl --cert-type P12 \
--cert ./sodexows.mo2o.com_client-android.p12:android \
https://sodexows.mo2o.com/
```
Response:
```json
{
    "code": 499,
    "msg": "No route found for \"GET /\"",
    "response": {}
}
```
It works! See how we could pass it the password `android` as defined in `resources/res/values/strings.xml`.
Until recently `curl` didn't support `P12`. Thankfully it's possible to convert it to PEM via `openssl`.
```sh
openssl pkcs12 -in assets/sodexows.mo2o.com_client-android.p12 \
-out sodexows.mo2o.com_client-android.key.pem -nocerts -nodes
openssl pkcs12 -in assets/sodexows.mo2o.com_client-android.p12 \
-out sodexows.mo2o.com_client-android.crt.pem -clcerts -nokeys
```
And use it with:
```sh
curl --cert ./sodexows.mo2o.com_client-android.crt.pem \
--key ./sodexows.mo2o.com_client-android.key.pem \
https://sodexows.mo2o.com/
```

## Endpoints
Now that we can access our host, we need to find the endpoints and play with it.
Unfortunately we cannot sniff network traffic with a Man-in-the-middle (e.g. via `mitmproxy`) because the app is expecting a specific server certificate. Hence we can't use a self-signed one and decrypt on the fly, see [HTTP Public Key Pinning](https://en.wikipedia.org/wiki/HTTP_Public_Key_Pinning).

We go back to the source code and throw some more `grep` to come across `sources/com/sodexo/app/data/api/service/Mo2oApiService.java`.
It contains 40+ endpoints, here's a couple:
```java
public interface Mo2oApiService {

    @POST("v3/connect/login")
    Call<LoginResponse> login(@Body LoginRequest loginRequest);

    @POST("v3/card/getCards")
    Call<GetCardsResponse> getCards(@Body GetCardsRequest getCardsRequest);
}
```

### v3/connect/login
First dumb try:
```sh
curl --cert-type P12 \
--cert ./sodexows.mo2o.com_client-android.p12:android \
https://sodexows.mo2o.com/v3/connect/login
```
Response:
```json
{
    "code": 499,
    "msg": "No route found for \"GET /v3/connect/login\"",
    "response": {}
}
```
No luck, we need to look into the code again for some kind of prefix.
Luckily we find `sources/com/sodexo/app/data/api/service/C2707a.java`.
```java
public class C2707a {

    @NonNull
    /* renamed from: a */
    private static Retrofit m8480a(OkHttpClient okHttpClient) {
        Retrofit.Builder builder = new Retrofit.Builder();
        StringBuilder sb = new StringBuilder();
        sb.append(f5094c);
        sb.append(Locale.getDefault().getLanguage());
        sb.append("/");
        return builder.baseUrl(
            sb.toString()).client(
                okHttpClient).addConverterFactory(
                    GsonConverterFactory.create(
                        new C2549g().mo18711a(
                            16, 128, 8).mo18710a())
            ).build();
    }
}
```
The important one is `sb.append(Locale.getDefault().getLanguage());`, see <https://developer.android.com/reference/java/util/Locale#getLanguage()>.
So the language (`ISO 639` format) is added to the base URL, e.g. `https://sodexows.mo2o.com/en`.
We can also see they're using the [OkHttp](https://square.github.io/okhttp/) client.
Back to our endpoint call.
```sh
curl --cert-type P12 \
--cert ./sodexows.mo2o.com_client-android.p12:android \
https://sodexows.mo2o.com/en/v3/connect/login
```
Response:
```json
{
    "code": 499,
    "msg": "No route found for \"GET /en/v3/connect/login\": Method Not Allowed (Allow: POST, OPTIONS)",
    "response": {}
}
```
The error message changed slightly to `Method Not Allowed (Allow: POST, OPTIONS)`.
We try again with a `POST` this time. Passing `--data` to `curl` would implicitly turn it to a `POST`.
```sh
curl --cert-type P12 \
--cert ./sodexows.mo2o.com_client-android.p12:android \
--data '' \
https://sodexows.mo2o.com/en/v3/connect/login
```
Response:
```json
{
    "code": 499,
    "msg": "Only JSON requests are allowed for this service set.",
    "response": {}
}
```
Another new error message, let's JSON then.
```sh
curl --cert-type P12 \
--cert ./sodexows.mo2o.com_client-android.p12:android \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--data '{}' \
https://sodexows.mo2o.com/en/v3/connect/login
```
Response:
```json
{
    "code": 999,
    "msg": "Se ha producido un error al guardar los datos, por favor int\u00e9ntalo de nuevo pasados unos minutos.",
    "response": {
        "errors": {
            "deviceUid": "This value should not be blank.",
            "os": "This value should not be blank.",
            "pass": "This value should not be blank.",
            "username": "This value should not be blank."
        }
    }
}
```
Bingo! Well I think that's it. This same info about fields can be found in `sources/com/sodexo/app/data/api/request/LoginRequest.java`.
```java
public class LoginRequest {
    private String deviceUid;

    /* renamed from: os */
    private int f5086os;
    private String pass;
    private String username;

    public LoginRequest(String str, String str2, String str3, int i) {
        this.username = str;
        this.pass = str2;
        this.deviceUid = str3;
        this.f5086os = i;
    }
}
```
Pretty explicit, but looking deeper in the source we can find out more about each parameters.
For instance for `deviceUid`, see `sources/com/sodexo/app/p083a/p084a/C2687a.java` file extract:
```java
Secure.getString(this.f5065a.getContentResolver(), "android_id");
```
It seems to be using [`Secure.ANDROID_ID`](https://developer.android.com/reference/android/provider/Settings.Secure.html#ANDROID_ID).
Now we can try to perform another call putting it all together.
```sh
deviceUid=whatever
os=0
username=foo@bar.com
pass=password
curl --cert-type P12 \
--cert ./sodexows.mo2o.com_client-android.p12:android \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--data '{"deviceUid": "'$deviceUid'", "os": '$os', "username": "'$username'", "pass": "'$pass'"}' \
https://sodexows.mo2o.com/en/v3/connect/login
```
Response:
```json
{
    "code": 100,
    "msg": "OK",
    "response": {
        "acepto_terminos": 1,
        "activated": 1,
        "beneficiaryCode": 12345,
        "cardCode4": "1234",
        "changePassword": 0,
        "cityJob": 0,
        "companyId": 12345,
        "complementaryDataJob": "",
        "dateBorn": "1987-06-05",
        "dateUp": "2017-05-22",
        "dni": "*HIDDEN*",
        "email": "*HIDDEN*",
        "gender": 0,
        "interestCollection": [
            {
                "idInteres": 0
            }
        ],
        "internalCode": 2,
        "matricula": "",
        "mobile": "*HIDDEN*",
        "name": "Andre",
        "nameAddressJob": "",
        "newsletter": 0,
        "password": "",
        "postalCodeJob": "*HIDDEN*",
        "securityDate": "*HIDDEN*",
        "stateJob": 0,
        "surname1": "Miras",
        "surname2": "Miras",
        "typeAddressJob": 0,
        "userData": {
            "city": 0,
            "complementaryData": "",
            "departmentId": 0,
            "functionId": 0,
            "hasChildren": 0,
            "nameAddress": "",
            "netIncomeId": 0,
            "postalCode": "",
            "state": 0,
            "typeAddress": 0,
            "typeWorkDay": 0,
            "userId": 12345
        }
    }
}
```
And voilà! Also note that a cookie is set (seen with `--verbose` flag):
```
Set-Cookie: PHPSESSID=deadbeef2827f09616128fe1d11fa5b7; path=/; secure
```

### v3/card/getCards
In a similar fashion we can reverse the other endpoints.
```sh
PHPSESSID=deadbeef2827f09616128fe1d11fa5b7
dni=*HIDDEN*
curl --cert-type P12 \
--cert ./sodexows.mo2o.com_client-android.p12:android \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--cookie "PHPSESSID=$PHPSESSID" \
--data '{"dni": "'$dni'"}' \
https://sodexows.mo2o.com/en/v3/card/getCards
```
Response:
```json
{
    "code": 100,
    "msg": "OK",
    "response": {
        "listCard": [
            {
                "arrFisToChange": [
                    {
                        "key": "BLOCKED",
                        "value": "60"
                    }
                ],
                "caducityDateCard": "",
                "cardNumber": "*HIDDEN*",
                "cardStatus": "ACTIVA",
                "fisToChangeState": "BLOCKED",
                "hasChip": 1,
                "idCard": 123456,
                "idCardStatus": "30",
                "idCompany": 12345,
                "idFisToChange": "60",
                "idProduct": 33,
                "pan": "*HIDDEN*",
                "programFis": "",
                "service": "Restaurante Pass"
            }
        ]
    }
}
```

### v2/card/getDetailCard
```sh
PHPSESSID=deadbeef2827f09616128fe1d11fa5b7
cardNumber=0123456789012345
curl --cert-type P12 --cert ./sodexows.mo2o.com_client-android.p12:android \
--header "Content-Type: application/json" \
--header "Accept: application/json" \
--cookie "PHPSESSID=$PHPSESSID" \
--data '{"cardNumber": "'$cardNumber'"}' \
https://sodexows.mo2o.com/en/v2/card/getDetailCard
```
Response:
```json
{
    "code": 100,
    "msg": "OK",
    "response": {
        "cardDetail": {
            "accountId": "",
            "addressReference": "",
            "arrFisToChange": [
                {
                    "key": "BLOCKED",
                    "value": "60"
                }
            ],
            "balanceFis": {
                "apuntesPendientes": 0,
                "saldoDisponible": 13.37
            },
            "blockedAmount": "",
            "caducityDateCard": "2022-12-31",
            "cardBalance": 13.37,
            "cardNumber": "*HIDDEN*",
            "cardStatus": "ACTIVA",
            "cardStatusDate": "2018-12-04",
            "creationDate": "",
            "dayRestriction": "",
            "description": "",
            "employeeName": "ANDRE MIRAS",
            "faceValue": 0,
            "fisToChangeState": "BLOCKED",
            "fromHour": "",
            "hasChip": 1,
            "idAddress": 0,
            "idBeneficiary": 0,
            "idCard": 123456,
            "idCardPayProvider": 0,
            "idCardStatus": "30",
            "idCompany": 12345,
            "idContract": 12345,
            "idCustomize": 0,
            "idFisToChange": "60",
            "idProduct": 33,
            "idProfile": 0,
            "infoBalanceRestriction": "",
            "itemType": 0,
            "legalNumber": "*HIDDEN*",
            "limitPassed": 0,
            "limiteConsumo": 0,
            "maxLoad": 0,
            "maxUsesDay": 0,
            "maxValueOfConsum": 0,
            "pan": "*HIDDEN*",
            "perfil": "",
            "printerName": "ANDRE MIRAS",
            "programFis": "SDSC",
            "timeRestriction": "",
            "toHour": "",
            "totalBalance": "",
            "useOnHoliday": ""
        }
    }
}
```

## Conclusion
So we seem to have covered point 1 & 2 of our motivations. How about point 3 then? I'll let you find out:
```sh
pip install mysodexo
mysodexo --balance
```
https://github.com/AndreMiras/mysodexo
