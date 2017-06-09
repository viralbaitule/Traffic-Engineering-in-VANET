Setup.
 
<b>In Mininet wifi vm :</b>
1.	Setting SSH Keys authentication between Mininet Wifi VM and floodlight VM<br />
  a.	ssh-keygen -t rsa<br />
  b.	cat ~/.ssh/id_rsa.pub | ssh username@192.168.56.107 "mkdir -p ~/.ssh && cat >>  ~/.ssh/authorized_keys"<br />
</t>where username is floodlight vm username and 192.168.56.107 is floodlight vm ip address
Tutorial : https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2
2.	<b>Modifying VANET.py File.<b>
  a.	Line no. 33: scp -o StrictHostKeyChecking=no rssi.json lubuntu@192.168.56.107:/home/lubuntu/Workspace > scp_out.txt<br />
Update appropriate floodlight/server vm username,ip address and destination directory.<br />
  b.	Line no. 64: c1 = net.addController( 'c1', controller=RemoteController, ip='192.168.56.107' )<br />
  <b>Change ip address In Floodlight VM</b><br />
3.	Open Eclipse floodlight creating The Listener module<br />
  a.	Add Class in Eclipse<br />
  b.	Expand the "floodlight" item in the Package Explorer and find the "src/main/java" folder.<br />
  c.	Right-click on th<br />e "src/main/java" folder and choose "New/Class".<br />
  d.	Enter "net.floodlightcontroller. srcdestiptracker" in the "Package" box.<br />
  e.	Enter " SrcDstIPTracker<br />" in the "Name" box.<br />
  f.	Next to the "Interfaces" box, choose "Add...".<br />
  g.	Add the "IOFMessageLi<br />stener" and the "IFloodlightModule", click "OK".<br />
  h.	Click "Finish" in the dialo<br />g.<br />
  i.	Copy the content of SrcDstIPTracker.java in created file.<br />
  j.	Save and exit eclipse.<br />

<b>Register the Module</b><br />
  a.	Open file src/main/resources/META-INF/services/net.floodlightcontroller.core.module.IFloodlightModule<br />
  b.	Add line “ net.floodlightcontroller.srcdestiptracker.SrcDstIPTracker ”<br />
  c.	Add line in floodlight.modules= “net.floodlightcontroller.srcdestiptracker.SrcDstIPTracker”<br />
  d.	Build floodlight “ant”<br />

4.	<b>get_traffic_statistics.py</b><br />
  a.	line no.211 :   with open('/home/lubuntu/Workspace/bandwidth.json', 'w') as bw:<br />
change path for file bandwith.json<br />
  b.	line no.213 :   with open('/home/lubuntu/Workspace/latency.json', 'w') as lat:<br />
change path for file latency.json<br />

5.	<b>Traffic_engineering.py</b><br />
  a.	update path for file bandwith.json, latency.json, rssi.json, rules.txt and data_for_graph.txt<br />
<br />
<b>Execution sequence:</b><br />
1.	floodlight: java -jar target/floodlight.jar<br />
2.	Mininet-wifi: (vanet.py): sudo python vanet.py<br />
3.	Floodlight vm (enable statistics collection): python get_link_statistics.py<br />
4.	Mininet-wifi (traffic generation): sudo ostinato<br />
Tutorial : http://ostinato.org/docs/ <br />
<br />
<b>Testing:</b><br />
1.	To Check utilized bandwidth do(Floodlight vm): cat bandwidth.json<br />
2.	To check link latency do(Floodlight vm): cat latency.json<br />
3.	To check car rssi value do(Floodlight vm): cat rssi.json<br />
4.	Algorithm testing:<br />
  a.	Ping between car<br /> 
  b.	Check generated rules in floodlight vm do: cat rules.txt<br />
  c.	Check pushed rules in Mininet-wifi console: dpctl dump-flows<br />

