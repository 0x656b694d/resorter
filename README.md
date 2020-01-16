# resorter
File organizer

# Examples

* append file names of .jpg and .JPG photos in the current directory with the camera maker:
```
$ resort move -if ext.low==".jpg" nam-exif_make+ext
wallpaper-SAMSUNG.jpg
photo-Sony.jpg
```

* print the file name if the date in the name (IMG_20162801_140410.jpg) does not correspond to the exif date:
```
$ resort -if "name[4,12]!=exif_time('%Y%m%d')"

```

* pass the source-destination pair to an external utility:
```
$ resort print '"nick@myserver:/files/"+name' | xargs -n 2 scp
```
