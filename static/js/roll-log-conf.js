var load_result;
var sel_ips=[];
window.onload = get_user_ips;
function getSelIp(){
	if(sel_ips.length>0){
		return sel_ips.join(',');
	}else{
		return null;
	}
}
function selectIt(obj){
	var fl=$(obj).attr("value");
	if(fl=='a'){
		$(obj).attr("value",'b');	
		var sel_p=$(obj).attr("data-value");
		sel_ips.push(sel_p);
	}else{
		var sel_p=$(obj).attr("data-value");
		delSelectIps(sel_p);
		$(obj).attr("value",'a');
	}
	$(obj).toggleClass("choose-selected");
}
function delSelectIps(ip){
	if(sel_ips.length>0){
		for(var i=0;i<sel_ips.length;i++){
			if(sel_ips[i]==ip){
				sel_ips.splice(i,1);
			}
		}
	}
}
function get_user_ips(){	
	$.post(site_url+"get_user_ips/",{
		'username':globle_username,
		},function(res){
			if (res.result && res.renum > 0) {	
				load_result=res.records;
				var apps = Object.keys(res.records);
				apps.sort();
				
				var select_apps = document.getElementById("select_apps");
				for (var i = 0; i < apps.length; i++) {
					var app_id = document.createElement("option");
					app_id.innerHTML = res.records[apps[i]]["app_name"];
					app_id.value = apps[i];
					select_apps.appendChild(app_id);
				}
				
				//将默认的第一个赋值IP
				var ips=res.records[apps[0]]["host_ip"];
				$.each(ips, function (n, value) {
		            $("#select_ips").append("<li title='"+n+"' value='a' data-value='"+n+"' onclick='selectIt(this);' class=''>"+n+"</li> ");
		        });
			}else {
				alert(res.text);
			}
		}, 'json');	  
 	}  

$(function() {
	//save-fo
	$("#bt_save").click(function(){
		var timeType=$("#timeType").val();//检查时间类型
		var timeNum=$("#timeNum").val();//检查时间参数
		var log_size=$("#log_size").val();//日志大小
		var log_path=$("#log_path").val();//-日志路径
		var select_ip=getSelIp();//检查选中IP
		var select_app=$("#select_apps").val();//app_name
		var dat="select_app:"+select_app+";select_ip:"+select_ip+";log_path:"+log_path+";log_size:"+log_size+";timeNum:"+timeNum+";timeType:"+timeType;
		if (select_ip==null || select_ip=='') { 
			layer.tips('<span style="color:red">选择IP不能为空</span>', '#select_ips',{tips:[1, '#E4E4E4'],time: 2000});
			$("#select_ips").focus();
			return; 
		}
		if (log_path==null || log_path=='') { 
			layer.tips('<span style="color:red">日志路径不能为空</span>', '#log_path',{tips:[1, '#E4E4E4'],time: 2000});
			$("#log_path").focus();
			return; 
		}
		if (!(/(^[1-9]\d*$)/.test(log_size))) { 
			layer.tips('<span style="color:red">日志大小为数字</span>', '#log_size',{tips:[1, '#E4E4E4'],time: 2000});
			$("#log_size").focus();
			return; 
		}
		if (!(/(^[1-9]\d*$)/.test(timeNum))) { 
			layer.tips('<span style="color:red">检查时间必须为整数</span>','#timeNum',{tips:[1, '#E4E4E4'],time: 2000});
			$("#timeNum").focus();
			return; 
		}
		var param={"select_app":select_app,"select_ip":select_ip,"log_path":log_path,"log_size":log_size,"timeNum":timeNum,"timeType":timeType};
		//alert(dat);
		
		var roll_cron_detail;
		if ( timeType =="day" ){
			roll_cron = timeNum*24*60*60;
			roll_cron_detail = timeNum+"天";
		}else if (timeType =="hour") {
			roll_cron = timeNum*60*60;
			roll_cron_detail = timeNum+"小时"
		}else{ //minute
			roll_cron = timeNum*60;
			roll_cron_detail = timeNum+"分钟"
		}		
		
		select_ip_arr = select_ip.split(',');		
		var ip_target = {};
		var apps = Object.keys(load_result);

		for (var i = 0; i < apps.length; i++) {
			var ips=load_result[apps[i]]["host_ip"];
			var ip = Object.keys(ips);
			for (var j = 0; j < ip.length; j++) {
				for (var k = 0; k < select_ip_arr.length; k++) {
					if (select_ip_arr[k] == ip[j]) {
						ip_target[ip[j]] = ips[ip[j]] 
					}					
				}
			}
		}			
		
		var biz_name = load_result[select_app]["app_name"];
		var selecedip = JSON.stringify(ip_target);
		
		$.post(site_url+"save_rolllog/",{
			'username':globle_username,
			'biz_id':select_app,
			'biz_name':biz_name,
			'biz_ip':selecedip,  //biz_ip:biz_ip_source
			'log_path':log_path,
			'log_size':log_size,
			'roll_cron':roll_cron,
			'roll_cron_detail':roll_cron_detail,			
			},function(res){
				if (res.result) {	
					alert(res.text);
				}else {
					alert(res.text);
				}
			}, 'json');	 
	});
	
	$("#select_apps").change(function(){
		 sel_ips=[]; //清空上一次选择
		 $("#select_ips").html("");
		 var sel=Number($("#select_apps").val());
		 var apps = Object.keys(load_result);
		 apps.sort();
		 for (var i = 0; i < apps.length; i++) {
			if(apps[i]==sel){
				var ips=load_result[apps[i]]["host_ip"];
				 $.each(ips, function (n, value) {
		            $("#select_ips").append("<li title='"+n+"' value='a' data-value='"+n+"' onclick='selectIt(this);' class=''>"+n+"</li> ");
		         });
			}
		 }
	});
});	

$(function() {
	$("#bt_cancel").click(function() {	
		sel_ips=[]; //清空上一次选择
		$("#select_ips li").each(function(){
			$(this).removeClass("choose-selected");
		});
//		$.post(site_url+"get_script_logs/",{
//		},function(res){
//			if (res.result) {
//				alert("ok");
//			}else {
//				alert(res.text);
//			}
//		}, 'json');			
	});
});