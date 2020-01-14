# resorter
File organizer

# Examples

* append file names of .jpg and .JPG photos in the current directory with the camera maker:
```
resort.py move -if ext.low==".jpg" nam-exif_make+ext
```

* print the file name if the date in the name (IMG_20162801_140410.jpg) does not corresponds to the exif date:
```
resort.py -if "name[4,12]!=exif_time('%Y%m%d')"
```
