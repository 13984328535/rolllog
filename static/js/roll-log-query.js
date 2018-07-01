window.onload = get_user_biz;
    
    function get_user_biz(){	
    	$.post(site_url+"get_user_biz/",{
    		'username':"${request.user.username}",
    		},function(res){
    			if (res.result && res.renum > 0) {	
    				load_result=res.records;
    				var biz_ids = Object.keys(res.records);
    				biz_ids.sort();
    				
    				var select_bizs = document.getElementById("select_bizs");
    				for (var i = 0; i < biz_ids.length; i++) {
    					var biz_id = document.createElement("option");
    					biz_id.innerHTML = res.records[biz_ids[i]];
    					biz_id.value = biz_ids[i];
    					select_bizs.appendChild(biz_id);
    				}
    			
    			}else {
    				alert(res.text);
    			}
    		}, 'json');	  
     	}  
    
      
	    $(function() {
	    	$("#bt_query").click(function() {	
	    		$("#rolllog_record").empty();
	    		var biz_id = $('#select_bizs option:selected').val();
	    		var biz_ip = $("#biz_ip").val().trim();
	    		var file_name = $("#file_name").val().trim();
	    		$.post(site_url+"get_roll_logs/",{
	    			'username':globle_username,
	    			'biz_id':biz_id,
	    			'biz_ip':biz_ip,
	    			'file_name':file_name,	    			
	    		},function(res){
	    			if (res.result) {
	    				records = JSON.parse(res.records);
	    				for (var i = 0; i < records.length; i++) {
		                    var row = document.getElementById("rolllog_record").insertRow();
		                    if(row!=null){
	                            cell=row.insertCell();
	                            cell.innerHTML=records[i].biz_name;
	                            cell = row.insertCell();
	                            cell.innerHTML=records[i].biz_ip;
	                            cell = row.insertCell();
	                            cell.innerHTML=records[i].log_path;
	                            cell = row.insertCell();
	                            cell.innerHTML=(records[i].log_size/1024/1024)+"M";	                            
	                            cell = row.insertCell();
	                            cell.innerHTML=(records[i].scan_time == "None"? "": records[i].scan_time);

	                            var scanExitCode = "检查文件异常"
	                            if (records[i].scan_result == -1) { scanExitCode = "未开始检查";
								}else if (records[i].scan_result == 3) { scanExitCode = "文件未生成";																
								}else{scanExitCode = "文件小于阀值";}
	                            
	                            cell = row.insertCell();
	                            cell.innerHTML=(records[i].scan_result == 3? scanExitCode:((records[i].scan_log_size == -1?"":((records[i].scan_log_size/1024/1024).toFixed(2)+"M")))) ;   	                            
	                            
	                            var doExitCode = "操作异常"
	                            if (records[i].do_result == -1) { doExitCode = "未操作";
								}else if (records[i].do_result == 0) { doExitCode = "操作正常";																
								}else{doExitCode = "操作异常";}
	                            
	                            cell = row.insertCell();
	                            cell.innerHTML=doExitCode;    
	                            cell = row.insertCell();
	                            cell.innerHTML=(records[i].do_time == "None"? "": records[i].do_time);    	                            
	                            cell = row.insertCell();
	                            cell.innerHTML='<input class="btn btn-danger" style="width: 55px;" value="删除" onclick="delIt(this,\''+records[i].id+'\');"/>'; 	                            	                            	                           
		                    }  	    						    				
						}

	    			}else {
	    				alert(res.text);
	    			}
	    		}, 'json');			
	    	});
	    });
	    
    
      function delIt(obj,id){
    	//询问框
    	  layer.confirm("删除后不可恢复!", {
    	    btn: ['确定','取消'] //按钮
    	  }, function(){
    		  layer.msg('正在删除..',{icon: 16,time: 6000,shade: 0.2});    		  
    		//执行删除
    		  $.post(site_url+"del_rolllog/",{"id":id},function(res){
    			    layer.closeAll('loading');
    			    layer.closeAll('dialog');
    				if (res.result) {
    					//删除成功后
    					$(obj).parent().parent().remove();//删除当前input所在行
    					alert(res.text);
    				}else {
    					alert(res.text);
    				}
    			}, 'json');	
    	  }, function(){
    		  //layer.msg('quxiao', {icon: 1});
    	  });
      }