@echo on
perfectoactions -c "<<CLOUD NAME, e.g. demo>>"  -d "model:Galaxy.*" -a "cleanup:false;get_network_settings:false" -s "<<TOKEN>>" 
EXIT /B