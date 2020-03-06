@echo on
perfectoactions -c "<<CLOUD NAME, e.g. demo>>"  -d "model:Galaxy.*" -a "cleanup:true;get_network_settings:true" -s "<<TOKEN>>" 
EXIT /B