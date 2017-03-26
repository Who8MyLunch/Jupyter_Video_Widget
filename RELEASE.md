# Release

## To release a new version of Jupyter_Video_Widget on PyPI:

Update _version.py (set release version, remove 'dev') and then:

```bash
git add <any new stuff>
git commit -a

python setup.py sdist upload
python setup.py bdist_wheel upload

git tag -a X.X.X -m 'comment'
```

Update _version.py (add 'dev' and increment minor) and then:

```bash
git commit -a

git push
git push --tags
```

## To release a new version of jupyter_video_widget on NPM:

Update version number in `js/src/package.json`. Clean working folders and publish:

```bash
git clean -fdx
npm install
npm publish
```
