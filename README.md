# 6G-SANDBOX TOOLKIT INSTALLER

Python3 script that configures an OpenNebula cluster as a 6G-SANDBOX site. 

## Pre-requirements

- An OpenNebula cluster with VMs internet access.
- Python3 and pip3 packages installed in the OpenNebula Frontend VMs.

## Requirements installation

```bash
pip3 install -r requirements.txt
```

## Running
The script execution must be performed in the OpenNebula Frontend using root user. This is due to the necessity of using the OpenNebula CLI tools and modifying core OpenNebula configurations. In future versions the possibility to use this tool remotely could be added.

Running the script:
```bash
python3 src/toolkit_installer.py
```

<details>
  <summary>Running phases</summary>
  
  ## Phase 1

  - Adding the 6GSandbox marketplace to OpenNebula if not present
  - Refreshing the list of available appliances in the marketplace

  ## Phase 2

  - Downloading base required appliances: Ubuntu, OneKE, 6GSANDBOX-core. The user is able to select version and datastore for each one.

  ## Phase 2.1

  - Instantiation of the 6GSANDBOX-core appliance. The user will be prompted for the required parameters. Pending to add further healthchecks.

  ## Phase 3

  - Donwloading and scanning the 6G Library repository for appliances
  - Matching the found appliances with the ones present in the 6G-SANDBOX Marketplace
  - Console dialog, asking the installer which component appliances  wants to import into the datastore. The appliances shown are the ones matching.


  ## Phase 4 => Pending

  - Create a form with information included in the SITES repository
    - ID of the networks
    - ID of the images
    - ID of the services
  - From a jinja template, generate the associated SITES file to be uploaded to private repo
  - Push the new site to github
    - TBD: You have to encrypt the info of the sites so that they are not seen with each other to avoid security flaws. This is easy using Ansible encrypt/decrypt. This way the repository can be made public, and we avoid additional configuration in Jenkins to clone and push private repos.
    - Each SITE must keep their master key to decrypt their file and configure it in their Jenkins

  ## Phase 5 => Pending

  - Launching a basic TN. A pipeline can be created in Jenkins, for the operator to enter and execute.
  - Validation and certification. Some testing.

