Setup.
 
In Mininet wifi vm :
1.	Setting SSH Keys authentication between Mininet Wifi VM and floodlight VM
  a.	ssh-keygen -t rsa
  b.	cat ~/.ssh/id_rsa.pub | ssh username@192.168.56.107 "mkdir -p ~/.ssh && cat >>  ~/.ssh/authorized_keys"
where username is floodlight vm username
and 192.168.56.107 is floodlight vm ip address
Tutorial : https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2
2.	Modifying VANET.py File.
  a.	Line no. 33: scp -o StrictHostKeyChecking=no rssi.json lubuntu@192.168.56.107:/home/lubuntu/Workspace > scp_out.txt
Update appropriate floodlight/server vm username,ip address and destination directory.
  b.	Line no. 64: c1 = net.addController( 'c1', controller=RemoteController, ip='192.168.56.107' )
Change ip address
In Floodlight VM
3.	Open Eclipse floodlight creating The Listener module
  a.	Add Class in Eclipse
  b.	Expand the "floodlight" item in the Package Explorer and find the "src/main/java" folder.
  c.	Right-click on the "src/main/java" folder and choose "New/Class".
  d.	Enter "net.floodlightcontroller. srcdestiptracker" in the "Package" box.
  e.	Enter " SrcDstIPTracker" in the "Name" box.
  f.	Next to the "Interfaces" box, choose "Add...".
  g.	Add the "IOFMessageListener" and the "IFloodlightModule", click "OK".
  h.	Click "Finish" in the dialog.
  i.	Copy the content of SrcDstIPTracker.java in created file.
  j.	Save and exit eclipse.

Register the Module
  a.	Open file src/main/resources/META-INF/services/net.floodlightcontroller.core.module.IFloodlightModule
  b.	Add line “ net.floodlightcontroller.srcdestiptracker.SrcDstIPTracker ”
  c.	Add line in floodlight.modules= “net.floodlightcontroller.srcdestiptracker.SrcDstIPTracker”
  d.	Build floodlight “ant”

4.	get_traffic_statistics.py
  a.	line no.211 :   with open('/home/lubuntu/Workspace/bandwidth.json', 'w') as bw:
change path for file bandwith.json
  b.	line no.213 :   with open('/home/lubuntu/Workspace/latency.json', 'w') as lat:
change path for file latency.json

5.	Traffic_engineering.py
  a.	update path for file bandwith.json, latency.json, rssi.json, rules.txt and data_for_graph.txt

Execution sequence:
1.	floodlight: java -jar target/floodlight.jar
2.	Mininet-wifi: (vanet.py): sudo python vanet.py
3.	Floodlight vm (enable statistics collection): python get_link_statistics.py
4.	Mininet-wifi (traffic generation): sudo ostinato
Tutorial : http://ostinato.org/docs/ 
Testing:
1.	To Check utilized bandwidth do(Floodlight vm): cat bandwidth.json
2.	To check link latency do(Floodlight vm): cat latency.json
3.	To check car rssi value do(Floodlight vm): cat rssi.json
4.	Algorithm testing:
  a.	Ping between car 
  b.	Check generated rules in floodlight vm do: cat rules.txt
  c.	Check pushed rules in Mininet-wifi console: dpctl dump-flows

