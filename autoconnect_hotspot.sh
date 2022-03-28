#!/bin/bash
while true
do
        if hotspotshield status | grep -q 'disconnected'
                then 
                        echo 'connecting ru vpn' && `hotspotshield connect ru` && sleep 10s
                else
                        echo 'still connected' && sleep  300s
        fi
done
