# Release

## To release a new version of Jupyter_Video_Widget on PyPI:

Update version number in file version.py and remove 'dev'.  Commit changes, upload to PyPI, add tag.

```bash
git add <any new stuff>
git commit -a

python setup.py sdist upload
python setup.py bdist_wheel upload

git tag -a X.X.X -m 'comment'
```

Once the above is done its time to go back to developing the next great release.  Update current version
number inside file version.py by adding 'dev' and increment minor number. Commit dev version and push new tags.

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
