# resorter
File organizer

# Examples

* append file names of .jpg and .JPG photos in the current directory with the camera maker:
```
$ resort move "if(ext.low=='.jpg', nam-exif_make+ext, none)"
wallpaper-SAMSUNG.jpg
photo-Sony.jpg
```

* print the file names and the exif time stamp if the date in the name (e.g. IMG_20162801_140410.jpg) does not correspond to the exif date:
```
$ resort print "if(name[0,3]=='IMG' && name[4,12]!=exif_time('%Y%m%d'), exif_time, none)"
IMG_20190729_102045.jpg '2019-08-03 13:40:00'

```

* pass the source-destination pair to an external utility:
```
$ resort print "'nick@myserver:/files/'+name" | xargs -n 2 scp
```

* add the artist name to the jpg images if made with Canon:
```
resort filter "if(ext=='.jpg' && exif_make=='Canon')" | xargs -n 1 exiv2 mo -M "set Exif.Image.Artist Vincent"
```

