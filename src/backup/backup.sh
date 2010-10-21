export PYTHONPATH='../'

rm -f *_data_archive.csv

appcfg.py download_data --config_file=loader_config.py --filename=program_data_archive.csv --kind=Program ../
appcfg.py download_data --config_file=loader_config.py --filename=project_data_archive.csv --kind=Project ../
appcfg.py download_data --config_file=loader_config.py --filename=gallery_data_archive.csv --kind=Gallery ../
appcfg.py download_data --config_file=loader_config.py --filename=image_data_archive.csv   --kind=Image ../

rm -fr bulkloader-*

