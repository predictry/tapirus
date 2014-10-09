#! /bin/bash


packer build  -var $aws_access_key -var $aws_secret_key EC2_MAIN_SERVER.json  >image_id.txt
ami=$(tail -n 1 image_id.txt | grep -E -o 'ami-.{8}')
rm $WORKSPACE/tapirus-config/image_id.txt


if [ ! -z "$ami" ]; then

current_launch_configuration=$(aws cloudformation describe-stack-resources --stack-name "update-tapirus" | grep -E -o 'update-tapirus-TapirusLaunchConfiguration-.+"' | grep -E -o '.+[^\"]')
	#updating the template
	aws cloudformation update-stack --stack-name update-tapirus --template-body file://tapirus.json --parameters  ParameterKey=Instanceid,ParameterValue=$ami

		counter=1
		while :;
  		do
  			update_status=$(aws cloudformation describe-stacks --stack-name "update-tapirus" | grep -E -o '"StackStatus": "(.+)"')

		if [[ $update_status == '"StackStatus": "UPDATE_COMPLETE"' ]]; then
			echo 'Stack successfully updated'

			#The below command will delete  the old image after the updating process finished
			aws ec2 deregister-image --image-id $old_ami_id
				
			echo $old_ami_id
				
			#The below command will get the ID of the snapshop from the old image
			snapshot_id=$(aws ec2 describe-snapshots | grep -E -A 10 "$old_ami_id.*" | grep -E -o 'snap-\S{8}')
				
			echo $snapshot_id

			#The bellow command will delete the the old snapshop
			aws ec2 delete-snapshot --snapshot-id $snapshot_id
	break
					else
						echo 'Updating is in process'
					 	counter=$(($counter + 1))
						echo $counter

					if [ $counter -eq 30 ]; then
						echo 'There is something wrong with updating the stack , please check out the stack events';
					break;
					fi
		sleep 10;
		fi
	done
else
echo "There is something wrong with packer"
return 1

fi

