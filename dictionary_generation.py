############################################################
#### generation of user's dictionary (configuration) #######
############################################################

import test_functions as test
import copy

def dictionary_generation(configure_file):

	#### loading configuration file
	
	configure = test.read_file_new(configure_file)
	
	config_file = open(configure_file,'rb')
	
	lines = config_file.readlines()
	
	config_file.close()
	
	lines = test.remove_all('\n',lines)
	
	fpm_dict = test.list_dict_trans(lines)
	
	############################################################
	#### generation of defaults's dictionary (configuration) ###
	############################################################		
	
	default_file = open('default_dictionary.txt','rb')
	
	lines_default = default_file.readlines()
	
	default_file .close()
	
	lines_default = test.remove_all('\n',lines_default)
	
	default_dict = test.list_dict_trans(lines_default)
	
	for key,values in default_dict.iteritems():
		
		if key not in fpm_dict:
			
			fpm_dict[key] = {}
	
	ref_separator = default_dict['ref_separator'][0]
	var_separator = default_dict['var_separator'][0]
	
	default_variable_list = default_dict['variable_list']
	
	fpm_variable_list = fpm_dict['variable_list']
	
	fpm_variable_list  = test.merge_lists(fpm_variable_list, default_variable_list )
	
	fpm_variable_dict = test.list_to_dict(fpm_variable_list, '=')
	
	fpm_dict['variable_list'] = fpm_variable_dict 
	
	####  #### some further transformation: ####  ####  
	
	### some variables for the timestep file
	
	default_name = ''
	
	#### generate operating files
	
	op_files_list = fpm_dict['op_files']
	op_files = []
	
	if op_files_list == {}:	
			
		print ''
		print '--> missing "op_files"'
		sys.exit('		~ Forgot to declare operating files?')
		
	else:	
		
		separator_files = default_dict['op_files'][0]
		
		op_files_dict = test.list_to_dict(op_files_list ,separator_files)
			
		fpm_dict['op_files'] = op_files_dict
	
	default = False
	
	for key, value in op_files_dict.iteritems():
		
		op_files.append(key)
		
		if value == 'default':
			
			op_files_dict['timestep_in_code_used_only_once'] = key 
			default = True
			break
	
	#### generate destination files
	
	destination_files_list =  fpm_dict['destination_files']
	
	if destination_files_list == {}:	
			
		destination_files_dict = {}
		
	else:	

		separator_dest = default_dict['destination_files'][0]
		
		destination_files_dict = test.list_to_dict(destination_files_list ,separator_dest)
	
		fpm_dict['destination_files'] = destination_files_dict
	
	
	separator_dest = default_dict['destination_files'][0]	
	
	#### configure variables
		
	var_list = fpm_dict['variables']
		
	if var_list == {}:	
		
		print ''
		print '--> missing "variables"'	
		sys.exit('		~ Forgot to declare variables?')
		
	else:	
		
		separator_var = default_dict['variables'][0]
		
		var_dict = test.list_to_dict(var_list ,'=')
		
		for key,value in var_dict.iteritems():
			
			var_dict[key] = test.str_to_list(value ,None,None, ref_separator)
		
		fpm_dict['variables'] = var_dict

	#### constraint_dictionary for constraints:
	
	constraint_dict = fpm_dict['check_constraints']
	
	## configure time check default's one
	
	constraint_default_dict = default_dict['check_constraints']			
	time_setup_default = constraint_default_dict['time_setup']		
	time_setup_default_dict = test.list_to_dict(time_setup_default,'=')	
	
	if constraint_dict == {}:
			
		time_setup_dict = time_setup_default_dict
				
		thread_dict = {}
		
		constraint_dict['threads'] = thread_dict
		constraint_dict['time_setup'] = time_setup_dict
	
		print ''
		print 'No constraints given. Program continues.'
		print ''
			
	else:	
			
		#### configure time setup
		
		try:
		
			time_setup = constraint_dict['time_setup']
			
		except:
				
			time_setup = []	
		
		time_setup_dict = test.list_to_dict(time_setup,'=')				
					
		for key,value in time_setup_default_dict.iteritems():
			
			if key in time_setup_dict:
				
				time_setup_dict[key] = float(time_setup_dict[key])
				
			else:
				
				try:
				
					time_setup_dict[key] = float(value)
				
				except:
					time_setup_dict[key] = value
				
		constraint_dict['time_setup'] = time_setup_dict ########## <<<<<--------
					
		#### configure threads:
		
		try:
		
			thread_dict = constraint_dict['threads'] 
		except:
			thread_dict = {} 	
			
		thread_default_dict = constraint_default_dict['threads']['thread_no']
		
		## preparing 'config' in thread_default_dict
		
		config = thread_default_dict['config']
		config_dict = test.list_to_dict(config,'=')
		
		for config_name,config_value in config_dict.iteritems():
				
			config_dict[config_name] = int(config_value)
		
		thread_default_dict['config'] = config_dict
			
		error_path = 'check_constraints -> threads -> '
		
		for thread,thread_value in thread_dict.iteritems():
			
			test.error_handling(thread_value,thread_default_dict ,error_path+thread)			
					
			for default_key,default_value in thread_default_dict.iteritems():
					
				if default_key in thread_value:
					
					if type(default_value) == list:
						
						separator = default_value[0]
						
						current_thread_conf = thread_value[default_key]
							
						current_thread_conf = test.list_to_dict(current_thread_conf,separator)
						
					#### check, if some more options have to be fulfilled:
							
					elif len(default_value) > 1:
						
						default_config = default_value
						
						current_thread_conf = thread_value[default_key]
						
						current_thread_conf = test.list_to_dict(current_thread_conf,'=')
		
						test.error_handling(current_thread_conf,default_config, error_path + thread + ' -> ' + default_key)
						
						for key,value in current_thread_conf.iteritems():
	
							current_thread_conf[key] = float(value)
								
						for defaults in default_config:
							
							if defaults not in current_thread_conf:
								
								try:
									
									current_thread_conf[defaults] = int(default_value[defaults])
								
								except:
									current_thread_conf[defaults] = default_value[defaults]
								
					thread_value[default_key] = current_thread_conf
								
				else:
						
					if len(default_value) > 1:
					
						thread_value[default_key]= default_value
						
					else:	
						
						thread_value[default_key] = {}
		
					
			arithm_dict = thread_value['arithmetics']
			control_dict= thread_value['control']
			
			
			arithm_dict,op_files_thread_arithm,var_dict_thread_arithm = test.replace_arguments(arithm_dict, var_dict, var_separator, '%s')
			
			var_dict = dict(var_dict.items() + var_dict_thread_arithm.items())
						
						
			control_dict,op_files_thread_control, var_dict_thread_control = test.replace_arguments(control_dict, var_dict, var_separator, '%s')						
								
			thread_value['variables'] = dict(var_dict_thread_control.items() + var_dict_thread_arithm.items())
			
			thread_value['op_files'] = test.merge_lists(op_files_thread_control, op_files_thread_arithm)
			
			thread_value['arithmetics'] = arithm_dict  
			thread_value['control'] = control_dict
			
		constraint_dict['threads'] = thread_dict ####################### <<<<<--------
	
		thread_amount = len(thread_dict) + 3
		
		fpm_dict['check_constraints'] = constraint_dict ####################### <<<<<--------

	#### direction of listed fpms:
	
	if fpm_dict['fpm_path'] == {}:
		
		fpm_dict['fpm_path'] = ''
		
	else:
		global_direction = fpm_dict['fpm_path'][0]	
		
		if global_direction[-1] != '/':
			
			global_direction += '/'
		
	fpm_dict['fpm_path'] = global_direction	
		
	#### list of analyzed fpms:
	
	if fpm_dict['fpm_to_be_analyzed'] == {}:
		
		print ''
		print 'No FPMs given. Proceeding is then impossible!'
		sys.exit('		~ Please write the names of the FPM you want to consider in the testing.')
		
	########## organising command structure
	
	#### prefix options:
	
	pre = fpm_dict['prefix_command']
	
	command_fpm = 	[]
	
	if pre == {}:
		
		pre = ''

		fpm_pos = 0
	else:
		pre = pre[0]
		pre_decomp = test.str_to_list(pre,None,None,' ')
		command_fpm.extend(pre_decomp)
		fpm_pos = len(pre_decomp)
		
	command_fpm.append('')
		
	#### suffix options:
	
	suff = fpm_dict['suffix_command']
	
	if suff == {}:
		
		suff = ''
		
	else:
		suff = suff[0]	
		suff_decomp = test.str_to_list(suff,None,None,' ')	
		command_fpm.extend(suff_decomp)
	
	command_fpm.append(fpm_pos)
	
	########## default's options settings	
	
	## default plot settings:
		
	picture_plot_options = default_dict['plots']['figure_file_name']['subplot_nr']['plot'] 
	parameter_options = default_dict['plots']['figure_file_name']['subplot_nr']['parameter']	
		
	picture_plot_options_dict = test.list_to_dict(picture_plot_options,'=')
	parameter_options_dict = test.list_to_dict(parameter_options,'=')	
	
	default_dict['plots']['figure_file_name']['subplot_nr']['plot'] = picture_plot_options_dict
	default_dict['plots']['figure_file_name']['subplot_nr']['parameter'] = parameter_options_dict	

	return fpm_dict,default_dict, command_fpm, default,op_files