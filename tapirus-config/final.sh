#! /bin/bash


packer build  -var $aws_access_key -var $aws_secret_key EC2_MAIN_SERVER.json  >image_id.txt
ami=$(tail -n 1 image_id.txt | grep -E -o 'ami-.{8}')
rm $WORKSPACE/pongo-config/image_id.txt


if [ ! -z "$ami" ]; then


	#updating the template
	if aws cloudformation update-stack --stack-name update-pongo --template-body file://cloud.json --parameters  ParameterKey=Instanceid,ParameterValue=$ami;then
			
		echo "The process finished successfully"
	else
        	echo "Updating the template failed"
        return 1

        fi

else
echo "There is something wrong with packer"
return 1

fi

