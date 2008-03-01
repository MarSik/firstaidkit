/*
* First Aid Kit - diagnostic and repair tool for Linux
* Copyright (C) 2008 Joel Andres Granados <jgranado@redhat.com>
*
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
*
*/


#include <Python.h>
#include <assert.h>
#include <string.h>
#include "parted/parted.h"

/*
 * Simple representation of the partition.
 */
typedef struct{
    int partnum;
    PedSector partstart;
    PedSector partend;
} partElem;


/*
 * Helper function
 */

/*
 * Returns a disk with the path of the device.
 */
static PedDisk *
_getDiskFromPath(char * path){
    PedDevice * dev;
    PedDisk * disk;
    /* Try to create the device with the path */
    dev = ped_device_get(path);
    if(dev == NULL)
        return NULL;

    /* Read the partition table off of the device */
    disk = ped_disk_new(dev);
    if(disk == NULL)
        return NULL;

    return disk;
}

/*
 * Return the partition type.
 */
static PedPartitionType
_disk_get_part_type_for_sector (PedDisk* disk, PedSector sector)
{
        PedPartition*   extended;

        extended = ped_disk_extended_partition (disk);
        if (!extended
            || !ped_geometry_test_sector_inside (&extended->geom, sector))
                return 0;

        return PED_PARTITION_LOGICAL;
}

/*
 * Create a python list from one partElement struct
 */
static PyObject *
_getPPartList( int partnum, int partstart, int partend ){
    PyObject * num, * start, * end;
    PyObject * list;
    /*
    * Create a new temporary list.  and add all the related values 
    */
    num = PyString_FromFormat("%d",partnum);
    start = PyLong_FromLong(partstart);
    end = PyLong_FromLong(partend);
    list = PyList_New(3);
    if(num == NULL || start == NULL || end == NULL ||
            list == NULL ||
            PyList_SetItem(list, 0, num) == -1 ||
            PyList_SetItem(list, 1, start) == -1 ||
            PyList_SetItem(list, 2, end) == -1){
        goto handle_error;
    }
    return list;

    handle_error:

    Py_XDECREF(num);
    Py_XDECREF(start);
    Py_XDECREF(end);
    Py_XDECREF(list);
    return NULL;
}

/*
 * Create a array of partElem with the python list
 */
static partElem
_getCPartList( PyObject * list ){
    partElem _list = {0};
    _list.partnum = -1;

    // check that its a list.
    if(!PyList_Check(list))
        return _list;

    // check that it has three elements.
    if(PyList_Size(list) < 3)
        return _list;

    // Populate the _partList array.
    _list.partnum = PyInt_AsLong( PyList_GetItem(list, 0) );
    _list.partstart = PyLong_AsLong( PyList_GetItem(list, 1) );
    _list.partend = PyLong_AsLong( PyList_GetItem(list, 2) );
    if( PyErr_Occurred())
        return _list;
    return _list;
}

static int MEGABYTE_SECTORS (PedDevice* dev)
{
        return PED_MEGABYTE_SIZE / dev->sector_size;
}


/*
 * Returns the partition if it is rescuable.  Null if nothing was done.
 */
static PedPartition *
rescuable(PedDisk * disk, PedSector start, PedSector end){

    //PedDisk * clone;
    PedSector s;
    PedGeometry * probed;
    PedGeometry sect_geom;
    PedGeometry entire_dev;
    PedPartition  * part = NULL;
    PedConstraint disk_constraint, * part_constraint;
    PedPartitionType part_type;
    PedFileSystemType * fs_type;

    /* Initialize the entire_dev geom for the contraint calculation */
    ped_geometry_init(&entire_dev, disk->dev, 0, disk->dev->length);
    part_type = _disk_get_part_type_for_sector (disk, (start + end) / 2);

    ped_exception_fetch_all(); //dont show errors

    for (s = start; s < end; s++) {

        /* Get a part from the specific s sector with the device constraint */
        ped_geometry_init (&sect_geom, disk->dev, s, 1);
        ped_constraint_init (&disk_constraint, ped_alignment_any, ped_alignment_any,
                &sect_geom, &entire_dev, 1, disk->dev->length);

        part = ped_partition_new (disk, part_type, NULL, s, end);
//printf("1\n");
        if(!part){
            ped_disk_remove_partition(disk, part);
            ped_constraint_done(&disk_constraint);
            part = NULL;
            continue;
        }

//printf("2\n");
        /* add the partition to the disk */
        if(!ped_disk_add_partition(disk, part, &disk_constraint)){
            ped_disk_remove_partition(disk, part);
            ped_constraint_done(&disk_constraint);
            part = NULL;
            continue;
        }

//printf("3\n");
        /* try to detect filesystem in the partition region */
        fs_type = ped_file_system_probe(&part->geom);
        if(!fs_type){
            ped_disk_remove_partition(disk, part);
            ped_constraint_done(&disk_constraint);
            part = NULL;
            continue;
        }

//printf("4\n");
        /* try to find the exact region the filesystem ocupies */
        probed = ped_file_system_probe_specific(fs_type, &part->geom);
        if(!probed){
            ped_disk_remove_partition(disk, part);
            ped_constraint_done(&disk_constraint);
            ped_geometry_destroy(probed);
            part = NULL;
            continue;
        }

//printf("5\n");
        /* see if probed is inside the partition region */
        if(!ped_geometry_test_inside(&part->geom, probed)) {
            ped_disk_remove_partition(disk, part);
            ped_constraint_done(&disk_constraint);
            ped_geometry_destroy(probed);
            part = NULL;
            continue;
        }

//printf("6\n");
        /* create a constraint for the probed region */
        part_constraint = ped_constraint_exact (probed);

//printf("7\n");
        /* set the region for the partition */
        if (!ped_disk_set_partition_geom (part->disk, part, part_constraint,
                                          probed->start, probed->end)) {
            ped_disk_remove_partition(disk, part);
            ped_constraint_done(part_constraint);
            ped_constraint_done(&disk_constraint);
            ped_geometry_destroy(probed);
            part = NULL;
            continue;
        }
//printf("8\n");
        break;
    }
    ped_exception_leave_all();// show errors.
//    if(part != NULL){
//        ped_constraint_done(part_constraint);
//        ped_constraint_done(&disk_constraint);
//        ped_geometry_destroy(probed);
//        ped_geometry_destroy(entire_dev);
//    }
    printf("returnrin\n");
    return part;
}

/*
 * Copy from parted.
 */
static int add_partition(PedPartition * part){
    const PedFileSystemType*        fs_type;
    PedGeometry*                    probed;
    PedExceptionOption              ex_opt;
    PedConstraint*                  constraint;
    char*                           found_start;
    char*                           found_end;

    fs_type = ped_file_system_probe (&part->geom);
    if (!fs_type)
            return 0;
    probed = ped_file_system_probe_specific (fs_type, &part->geom);
    if (!probed)
            return 0;

    if (!ped_geometry_test_inside (&part->geom, probed)) {
            ped_geometry_destroy (probed);
            return 0;
    }

    constraint = ped_constraint_exact (probed);
    if (!ped_disk_set_partition_geom (part->disk, part, constraint,
                                      probed->start, probed->end)) {
            ped_constraint_destroy (constraint);
            return 0;
    }
    ped_constraint_destroy (constraint);

    found_start = ped_unit_format (probed->dev, probed->start);
    found_end = ped_unit_format (probed->dev, probed->end);

    ped_partition_set_system (part, fs_type);
    ped_disk_commit (part->disk);
    return 1;
}

/* Pythong facing functions.
 *
 * Returns a dictionary of the form { DISK : [None, None, None, None] ...}
 */
static PyObject *
undelpart_getDiskList(PyObject * self, PyObject * args){

    PedDevice * dev;

    PyObject * dict;
    PyObject * list;
    PyObject * diskName;

    int i;

    dict = PyDict_New();
    if(dict == NULL){
        PyErr_SetString(PyExc_StandardError, "Error creating a new dictionary.");
        goto handle_error;
    }

    /* Search for the disks on the system */
    ped_device_probe_all();

    for(dev=ped_device_get_next(dev); dev ; dev=ped_device_get_next(dev)){
        /*
         * Build the list for this particular disk and fill it with Python
         * None Objects. 
         */
        list = PyList_New(4);
        if(list == NULL){
            PyErr_SetString(PyExc_StandardError, "Error creating a new list.");
            goto handle_error;
        }
        for(i=0 ; i < 4 ; i++){ //We set all items to None.
            if(PyList_SetItem(list, i, Py_None) == -1){
                PyErr_SetString(PyExc_StandardError,
                        "Error setting up the None valued list.");
                goto handle_error;
            }
        }

        /*
         * Take the name out of the PedDevice structure and place it as a
         * dictionary key.  Use the device path.
         */
        diskName = Py_BuildValue("s", dev->path);
        if(diskName == NULL){
            PyErr_SetString(PyExc_StandardError,
                    "Error creating key for dictionary.");
            goto handle_error;
        }

        if(PyDict_SetItem(dict, diskName, list) == -1){
            PyErr_SetString(PyExc_StandardError,
                    "Error while creating the dictionary entry");
            goto handle_error;
        }
    }

    /* If the dictionary's length is 0, something is wrong. */
    if(PyDict_Size(dict) == 0){
        PyErr_SetString(PyExc_StandardError,
                "libparted was unable to get a disk list. Are you root?");
        goto handle_error;
    }

    return dict;

    handle_error:
    assert(PyErr_Occurred());

    Py_XDECREF(diskName);
    Py_XDECREF(list);
    Py_XDECREF(dict);

    return NULL;
}

/*
 * Returns a list of partitions that are present in the disk but not in its
 * partition table. If the disk does not exist it returns None. If the disk
 * has no rescueable partitions it returns a void list.  Most of this is
 * a copy of the parted code.
 */
static PyObject *
undelpart_getRescuable(PyObject * self, PyObject * args){

    PedDisk  * disk, * clone;
    PedDevice * dev;
    PedPartition * part;
    PedPartition * recoverablePart = NULL;
    PedSector current, start, end;

    PyObject * tempList;
    PyObject * partitions;

    char * path;

    if(!PyArg_ParseTuple(args, "s", &path)){
        PyErr_SetString(PyExc_TypeError, "Argument is not a String");
        goto handle_error;
    }

    /* Build the empty list*/
    partitions = PyList_New(0);
    if(partitions == NULL){
        PyErr_SetString(PyExc_StandardError, "Error creating a new list.");
        goto handle_error;
    }

    /* create the disk an dev */
    disk = _getDiskFromPath(path);
    if(disk == NULL){
        PyErr_SetString(PyExc_StandardError, "Error reading disk information.");
        goto handle_error;
    }
    dev = disk->dev;

    /*
     * We start looking for the partitions.  The partitions will be detected if
     * it contains a filesystem.  The basic idea is to traverse all the partitions
     * and look for holes in between.  When a hole is found, we look for a
     * partition inside the hole.
     */
    start = (PedSector)0;
    current = start;
    end = dev->length;
    part = ped_disk_next_partition(disk, NULL);
    while(part){

        /* We clone the disk to avoid strangeness in the loop with the disk object */
        clone = ped_disk_duplicate(disk);
        if(clone == NULL){
            part = ped_disk_next_partition(disk, part);
            continue;
        }

        printf(" current %d, part->geomS %d, part->geom %d, num %d\n", current, part->geom.start, part->geom.end, part->num);
        if(part->num == -1 && part->geom.start < part->geom.end){
            /* There might be a partition between current and part->geom.start */
            recoverablePart = rescuable(clone, part->geom.start, part->geom.end);
            //printf("after the rescuable\n");
            if(recoverablePart != NULL){
                /* create the python object */
                tempList = _getPPartList(recoverablePart->num,
                        recoverablePart->geom.start,
                        recoverablePart->geom.end);
                /* Append the list to the return value */
                if(tempList == NULL || PyList_Append(partitions, tempList) == -1){
                    PyErr_SetString(PyExc_StandardError,
                            "Error creating the partition information.");
                    goto handle_error;
                }
                /* free used objects */
                ped_disk_remove_partition(clone, recoverablePart);
                ped_disk_destroy(clone);
                recoverablePart = NULL;
                clone = NULL;
            }
        }
        //printf("next partitino\n");
        part = ped_disk_next_partition(disk, part);
    }

    if(disk != NULL)
        ped_disk_destroy(disk);

    return partitions;

    handle_error:
    assert(PyErr_Occurred());

    if(disk != NULL )
        ped_disk_destroy(disk);

    Py_XDECREF(partitions);
    Py_XDECREF(tempList);

    return NULL;
}

/*
 * Returns a list of valid partitions at time of scan.
 */
static PyObject *
undelpart_getPartitionList(PyObject * self, PyObject * args){

    PedDisk * disk;
    PedDevice * dev;
    PedPartition * part; //libparted object

    PyObject * partList; //python list of partitions
    PyObject * tempList; //python temporary object to hold the temprorary list.

    char * path;

    if(!PyArg_ParseTuple(args, "s", &path)){
        PyErr_SetString(PyExc_TypeError, "Argument is not a String");
        goto handle_error;
    }

    /* create the disk an dev */
    disk = _getDiskFromPath(path);
    if(disk == NULL){
        PyErr_SetString(PyExc_StandardError, "Error reading disk information.");
        goto handle_error;
    }
    dev = disk->dev;

    /* Create the python list that we are to fill */
    partList = PyList_New(0);
    if(partList == NULL){
        PyErr_SetString(PyExc_StandardError, "Error creating a new list.");
        goto handle_error;
    }

    /* Get all the active partitions from disk */
    for(part = ped_disk_next_partition(disk, NULL) ;
            part ; part = ped_disk_next_partition(disk, part)){
        if(part->num < 0)
            continue;

        tempList = _getPPartList(part->num,
                part->geom.start,
                part->geom.end);
        /* Append the list to the return value */
        if(tempList == NULL || PyList_Append(partList, tempList) == -1){
            PyErr_SetString(PyExc_StandardError,
                    "Error appending the partition to the list.");
            goto handle_error;
        }
    }

    return partList;

    handle_error:
    assert(PyErr_Occurred());

    Py_XDECREF(partList);
    Py_XDECREF(tempList);

    return NULL;
}

/*
 * Set the partition table for a specific disk.  It recieves a part number and
 * start and end sectors for a specific partitions.  If the partition is in
 * the list but not in the system, the function will try to add it.  If the
 * partition is in the system but not in the table, it will be removed.
 * The object recieved must be (string), [[(string), ing, int],...]
 */
static PyObject *
undelpart_setPartitionList(PyObject * self, PyObject * args){

    PedPartitionType part_type;
    PedDisk * disk;
    PedDevice * dev;
    PedPartition * part; //individual partitions.

    PyObject * partList; //list of partitions.
    PyObject * tempList;
    PyObject * partNum, * partStart, * partEnd;

    partElem * _partList; //Resulting list from the python object.
    partElem * _partListSystem; //partitions that are in the system.
    int partListSize = 0; //The size of both python and local lists.
    int i,j;
    int inTheList, inTheSystem;
    char * path;

    /* Check the arguments */
    if(!PyArg_ParseTuple(args, "sO", &path, &partList)){
        PyErr_SetString(PyExc_TypeError, "Arguments passed are of the wrong type.");
        goto handle_error;
    }
    if(! PyList_Check(partList)){
        PyErr_SetString(PyExc_TypeError, 
                "The object that was passed is not a list.");
        goto handle_error;
    }

    /* Put the values of the list into a array of partElem */
    partListSize = PyList_Size(partList);
    _partList[partListSize+1];
    for(i=0; i < partListSize ; i++){
        _partList[i] = _getCPartList(PyList_GetItem(partList, i));
        if( PyErr_Occurred() || _partList[i].partnum == -1 )
            goto handle_error;
    }
    _partList[partListSize].partnum = '\0';

    /* create the disk an dev */
    disk = _getDiskFromPath(path);
    if(disk == NULL){
        PyErr_SetString(PyExc_StandardError, "Error reading disk information.");
        goto handle_error;
    }
    dev = disk->dev;

    /* Travers all the disks and erase the ones that are not on the list */
    inTheList = 0;
    _partListSystem[partListSize+1];
    _partListSystem[0].partnum = '\0';
    j=0; //it will be the offset of _partListSystem
    for(part = ped_disk_next_partition(disk, NULL) ;  part ; 
            part = ped_disk_next_partition(disk, part)){
        if(part->num < 0)
            continue;

        /*look at the list*/
        for(i=0 ; _partList[i].partnum != '\0' ; i++){
            if(part->num == _partList[i].partnum){
                inTheList = 1;
                _partListSystem[j] = _partList[i];
                _partListSystem[++j].partnum = '\0';
                break;
            }
        }

        if(! inTheList){
            if(ped_disk_remove_partition(disk, part)){
                PyErr_SetString(PyExc_StandardError,
                        "Could not remove partition from disk.");
                goto handle_error;
            }
        }
        inTheList = 0;
    }

    /* Travers all the disks and erase the ones that are not on the system */
    inTheSystem = 0;
    for(i=0; _partList[i].partnum != '\0' ; i++){
        for(j=0; _partListSystem[j].partnum != '\0' ; j++){
            if(_partList[i].partnum == _partListSystem[j].partnum){
                inTheSystem = 1;
                break;
            }
        }

        if(! inTheSystem){
            /* try to add the partition */

            part_type = _disk_get_part_type_for_sector(disk,
                    (_partList[i].partstart + _partList[i].partend) /2 );
            part = ped_partition_new (disk, part_type, NULL,
                    _partList[i].partstart, _partList[i].partend);
            if(part)
                add_partition(part);
            inTheSystem=0;
        }
    }

    return Py_True;

    handle_error:

    assert(PyErr_Occurred());

    return NULL;
}

/*
 * On a specific disk try to rescue a list of partitions.  Return the list of partitions
 * that was recovered.  The partitions should be in the [[partNum, start, end]...]
 * format.
 */
static PyObject *
undelpart_rescue(PyObject * self, PyObject * args){

    PedDisk * disk;
    PedDevice * dev;
    PedPartition * part;
    PedPartitionType part_type;

    PyObject * partList;
    PyObject * rescuedParts;
    PyObject * tempList;
    PyObject * partNum, * partStart, *partEnd;

    partElem * _partList;
    char * path;
    int partListSize;
    int i;

    /* Check the arguments */
    if(!PyArg_ParseTuple(args, "sO", &path, &partList)){
        PyErr_SetString(PyExc_TypeError, "Arguments are not valid (String, [])");
        goto handle_error;
    }
    if(! PyList_Check(partList)){
        PyErr_SetString(PyExc_TypeError,
                "The object that was passed is not a list.");
        goto handle_error;
    }

    /* Build the empty list, this is the return value. */
    rescuedParts = PyList_New(0);
    if(rescuedParts == NULL){
        PyErr_SetString(PyExc_StandardError, "Error creating a new list.");
        goto handle_error;
    }

    /* Put the values of the list into a array of partElem */
    partListSize = PyList_Size(partList);
    _partList[partListSize+1];
    for(i=0; i < partListSize ; i++){
        _partList[i] = _getCPartList(PyList_GetItem(partList, i));
        if( PyErr_Occurred() || _partList[i].partnum == -1)
            goto handle_error;
    }
    _partList[partListSize].partnum = '\0';

    /* create the disk an dev */
    disk = _getDiskFromPath(path);
    if(disk == NULL){
        PyErr_SetString(PyExc_StandardError, "Error reading disk information.");
        goto handle_error;
    }
    dev = disk->dev;

    /* Try to add each partition. */
    for(i=0 ; i < partListSize ; i++){
        part_type = _disk_get_part_type_for_sector(disk,
                (_partList[i].partstart + _partList[i].partend) /2 );
        part = ped_partition_new (disk, part_type, NULL,
                _partList[i].partstart, _partList[i].partend);
        if(part && add_partition(part)){
            tempList = _getPPartList(part->num, part->geom.start, part->geom.end);
            /* Append the list to the return value */
            if(tempList == NULL || PyList_Append(rescuedParts, tempList) == -1){
                PyErr_SetString(PyExc_StandardError,
                        "Error creating the partition information.");
                goto handle_error;
            }
        }
    }

    return rescuedParts;

    handle_error:
    assert(PyErr_Occurred());

    return NULL;
}

static struct PyMethodDef undelpart_methods [] = {
    { "getDiskList",
        (PyCFunction)undelpart_getDiskList,
        METH_VARARGS, "Generaly returns the system disk list.  Receives nothing." },
    { "getRescuable",
        (PyCFunction)undelpart_getRescuable,
        METH_VARARGS, "Get a list of partitions from a specific disk that might "
            "be rescuable.  It returns the partitions that are not in the partition "
            "table but where present after a disk scan.  It expects the disk name."},
    { "getPartitionList",
        (PyCFunction)undelpart_getPartitionList,
        METH_VARARGS, "Get the partition list off of a certain disk.  This is intended "
            "to be used as a backup.  It returns the number of the partition, start "
            "sector and the end sector."},
    { "setPartitionList",
        (PyCFunction)undelpart_setPartitionList,
        METH_VARARGS, "This does NOT add new partitions to the disk.  It scans the "
            "disk and deletes partitions that are in the disk partition table but "
            "not in the list."},
    { "rescue",
        (PyCFunction)undelpart_rescue,
        METH_VARARGS, "Try to put the list of rescuable partitions into the partition "
            "table.  If the partitions are already there, nothing will be done.  A list "
            "of rescued partitions is returned.  This does NOT delete any partitions."}
};

void init_undelpart(void){
    (void) Py_InitModule("_undelpart", undelpart_methods);
}