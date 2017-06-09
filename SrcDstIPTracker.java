package net.floodlightcontroller.srcdestiptracker;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.util.Collection;
import java.util.HashSet;
import java.util.Map;

import org.projectfloodlight.openflow.protocol.OFMessage;
import org.projectfloodlight.openflow.protocol.OFType;
import org.projectfloodlight.openflow.types.EthType;
import org.projectfloodlight.openflow.types.IPv4Address;

import net.floodlightcontroller.core.FloodlightContext;
import net.floodlightcontroller.core.IOFMessageListener;
import net.floodlightcontroller.core.IOFSwitch;
import net.floodlightcontroller.core.module.FloodlightModuleContext;
import net.floodlightcontroller.core.module.FloodlightModuleException;
import net.floodlightcontroller.core.module.IFloodlightModule;
import net.floodlightcontroller.core.module.IFloodlightService;
import net.floodlightcontroller.core.IFloodlightProviderService;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentSkipListSet;
import java.util.Set;
import net.floodlightcontroller.packet.Ethernet;
import net.floodlightcontroller.packet.IPv4;


public class SrcDstIPTracker implements IOFMessageListener, IFloodlightModule {
	protected IFloodlightProviderService floodlightProvider;
	protected Set<Long> srcIpAddress;
	protected Set<Long> dstIpAddress;
	HashSet<String> hSet = new HashSet<String>();
	HashSet<String> hashCars = new HashSet<String>(){/**
		 * new added
		 */
		private static final long serialVersionUID = 1L;

	{
	    add("192.168.0.1");
	    add("192.168.0.2");
	    add("192.168.0.3");
	    add("192.168.0.4");
	}};
	

	@Override
	public String getName() {
		return SrcDstIPTracker.class.getSimpleName();
	}

	@Override
	public boolean isCallbackOrderingPrereq(OFType type, String name) {
		return false;
	}

	@Override
	public boolean isCallbackOrderingPostreq(OFType type, String name) {
		return false;
	}

	@Override
	public Collection<Class<? extends IFloodlightService>> getModuleServices() {
		return null;
	}

	@Override
	public Map<Class<? extends IFloodlightService>, IFloodlightService> getServiceImpls() {
		return null;
	}

	@Override
	public Collection<Class<? extends IFloodlightService>> getModuleDependencies() {
		Collection<Class<? extends IFloodlightService>> l =
	        new ArrayList<Class<? extends IFloodlightService>>();
	    l.add(IFloodlightProviderService.class);
	    return l;
		
	}

	@Override
	public void init(FloodlightModuleContext context)
			throws FloodlightModuleException {
		floodlightProvider = context.getServiceImpl(IFloodlightProviderService.class);
		srcIpAddress = new ConcurrentSkipListSet<Long>();
		dstIpAddress = new ConcurrentSkipListSet<Long>();

	}

	@Override
	public void startUp(FloodlightModuleContext context)
			throws FloodlightModuleException {
		floodlightProvider.addOFMessageListener(OFType.PACKET_IN, this);
	}

	@Override
	public net.floodlightcontroller.core.IListener.Command receive(
			IOFSwitch sw, OFMessage msg, FloodlightContext cntx) {
		Ethernet eth =IFloodlightProviderService.bcStore.get(cntx,IFloodlightProviderService.CONTEXT_PI_PAYLOAD);
        if (eth.getEtherType() == EthType.IPv4) {
            /* We got an IPv4 packet; get the payload from Ethernet */
            IPv4 ipv4 = (IPv4) eth.getPayload();
             
            /* Various getters and setters are exposed in IPv4 */
            byte[] ipOptions = ipv4.getOptions();
            IPv4Address dstIp = ipv4.getDestinationAddress();
            IPv4Address srcIp = ipv4.getSourceAddress();
            if (hashCars.contains(new String(srcIp.toString())) && hashCars.contains(new String(dstIp.toString()))){
	            if (!(hSet.contains(new String(srcIp.toString())) && hSet.contains(new String(dstIp.toString())))){
	            	hSet.add(new String(srcIp.toString()));
	            	hSet.add(new String(dstIp.toString()));
	            	try  {
            			
            			Process process = Runtime.getRuntime().exec(String.format("python /home/lubuntu/Workspace/node.py %s %s > /home/lubuntu/Workspace/cmd_viral.log",srcIp.toString(),dstIp.toString()));
	                    File newTextFile = new File("/home/lubuntu/Workspace/thetextfile.txt");
	                    FileWriter fw = new FileWriter(newTextFile,true);
	                    fw.write("Source IP: ");
	                    fw.write(srcIp.toString());
	                    fw.write("\t");
	                    fw.write("Destination IP: ");
	                    fw.write(dstIp.toString());
	                    fw.write('\n');
	                    fw.close();
                	} 
                catch (IOException e) {
                		new RuntimeException("Error message", e).printStackTrace();
                	}
	            }
	            else{
	            	hSet.remove(srcIp.toString());
	            	hSet.remove(dstIp.toString());
	            }
            }
        }
        return Command.CONTINUE;
	}

}
