<div align="center">
    <img src="./flask_app/dash_app/assets/assas_logo.svg" height="300px"></img>
</div>

-----------

# ASSAS Data Hub

The ASSAS Data Hub is a web application to store and visualize ASTEC simulation data on the Large Scale Data Facility at KIT. Its database contains the ASTEC archive in binary raw format and offers a conversion in other data formats.

- [Installation](#installation)
- [Upload ASTEC data](#upload-astec-data)

## Installation

### Start application

Entrypoint of the application is wsgi.py (Python Web Server Gateway Interface)

### NoSQL Database

### Mount lsdf share

```console
$ sudo mount -t cifs -o vers=2.0,username='ke4920',uid=$(id -u),gid=$(id -g) //os.lsdf.kit.edu/kit/scc/projects/ASSAS /mnt/ASSAS
```

## Upload ASTEC data

The upload of ASTEC data is supported through an upload application under ``tools/assas_data_uploader.py``. The use of the upload application requires the following:

1. Create Partner- and Guest-KIT Account
2. Access to the LSDF with this account
3. Installation of ``Python3.10+`` and ``rysnc``
4. Define the ASTEC archive directory tree

The commandline interface of the upload application requires the following parameter:

* --user: KIT internal batch which has access to the LSDF
* --source: Path to the directory tree which will be uploaded (ASTEC Project directory)
* --archive: Sub path to the actual ASTEC archive inside the directory tree, or a list of sub paths 

<div align="center">
    <img src="./flask_app/dash_app/assets/assas_data_upload.png" height="200px"></img>
</div>