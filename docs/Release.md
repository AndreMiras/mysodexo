# How to release

This is documenting the release process.

We're using [calendar versioning](https://calver.org/) where `YYYY.MM.DD` should be set accordingly.

```sh
VERSION=YYYY.MM.DD
```

## Start the release

```sh
git checkout -b release/$VERSION
```

Now update the [setup.py](../setup.py) `version` to match the new release version.

```sh
SANITIZED_VERSION=$(echo $VERSION | sed 's/\.//g')
sed --regexp-extended 's/"version": "(.+)"/"version": "'$SANITIZED_VERSION'"/' --in-place setup.py
```

Then commit/push and create a pull request targeting the `main` branch.

```sh
git commit -a -m ":bookmark: $VERSION"
git push origin release/$VERSION
```

Once the pull requests is approved/merged, tag the `main` branch with the version.
In the case of a sole owner, no pull request is required, but at least verify the CI builds green.

```sh
git checkout main
git pull
git tag -a $VERSION -m ":bookmark: $VERSION"
git push --tags
```

## Publish to PyPI

This process is handled automatically by [GitHub Actions](https://github.com/AndreMiras/mysodexo/actions/workflows/pypi-release.yml).
If needed below are the instructions to perform it manually.
Build it:

```sh
make release/build
```

Check archive content:

```sh
tar -tvf dist/mysodexo-*.tar.gz
```

Upload:

```sh
make release/upload
```

This will also publish the alias meta package `setup_meta.py`.

## Release notes

You may want to add some GitHub release notes, by attaching a release to
[the newly pushed tag](https://github.com/AndreMiras/mysodexo/tags).

## Check Read the Docs

Make sure <https://readthedocs.org/projects/mysodexo/> is up to date.

## GitHub

Got to GitHub [Release/Tags](https://github.com/AndreMiras/mysodexo/tags), click "Add release notes" for the tag just created.
Add the tag name in the "Release title" field and the relevant CHANGELOG.md section in the "Describe this release" textarea field.
Finally, attach the generated APK release file and click "Publish release".
