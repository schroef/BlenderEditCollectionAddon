# Blender "Edit Instanced Collection" Addon
An add-on for Blender that allows quickly editing Collection Instance source collections.

This came about as the result of making Asset Library files that used Collection Instances to house multiple-Object assets.
Upon importing them into another file, they would be seemingly uneditable, as Blender would link the Collection Instances to
the current Scene, but not the Collection itself.

Since it was a relatively reproducible process to find and link the Collections, I created this addon that allows quickly
dropping in to edit the underlying Collection of a Collection Instance, and then dropping out.

## To install

Either install the ZIP file from the release or clone this repository and use the
build_release.py script to build a ZIP file that you can install into Blender.

## To Use

1. Select a Collection Instance. (Selecting multiple Collection Instances is not supported.)
2. Either from the Object menu or the spacebar/W context menu, select "Edit Instanced Collection", or use the hotkey (Ctrl+Alt+C)
   in Object Mode. In the panel (N) > Item > Edit Instance Collection. We see buttons depending on the hierarchy.
3. You will be dropped into a newly-created Scene containing nothing but the Collection. Edit the collection, and your
   edits will be reflected in all instances of the Collection.
4. In the panel (N) > Item > Edit Instance Collection. We see buttons depending on the hierarchy.
   When there are nested Collection, we see again "Edit Collection", so we can go deeper into hierarchy
5. Once in say level 2, we see a button "Previous Collection", this will return to the prior Collection
   There is also a button "Return to Main Scene".
6. Each time you return, the temp scene will automatically be deleted.
   When "Return to Main Scene" is used, all tmp scenes will be deleted.

You can drill down to multiple levels, though you will have to be sure to clean up any temporary Scenes and Worlds
made by the addon (usually, using the Clean Up tools).
