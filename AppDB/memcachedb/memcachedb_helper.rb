require 'djinn'
require 'djinn_job_data'
require 'helperfunctions'

DB_PORT = 30000
DB_LOCATION = "/var/appscale/memcachedb"

def get_uaserver_ip()
  Djinn.get_nearest_db_ip
end

def get_db_ports
  [DB_PORT, 31000]
end

def has_soap_server?(job)
  return true if job.is_db_master? || job.is_db_slave?
  return false
end

def setup_db_config_files(master_ip, slave_ips, creds)
  # nothing to do
end

def start_db_master()
  @state = "Starting up MemcacheDB"
  Djinn.log_debug("Starting up MemcacheDB as Master")

  my_ip = my_node.private_ip
  n = @creds['replication']

  Djinn.log_debug("Starting memcachedb master at ip #{my_ip} and replication #{n}")

  if restore_from_db?
    Kernel.system "rm -rf #{DB_LOCATION}"
    if @creds['restore_from_tar']
      restore_db_from_tar
    elsif @creds['restore_from_ebs']
      restore_db_from_ebs
    end
   else
    Djinn.log_debug(`rm -rf #{DB_LOCATION}*`)
    Kernel.system "mkdir -p #{DB_LOCATION}"
  end

  Kernel.system "memcachedb -p #{DB_PORT} -u root -d -r -H #{DB_LOCATION} -N -R #{my_ip}:31000 -M -n #{n} >> #{DB_LOCATION}/memcachedb.log 2>&1 &"
  HelperFunctions.sleep_until_port_is_open(my_ip, DB_PORT)
end

def stop_db_master
  Djinn.log_debug("Stopping MemcacheDB as master")
  Djinn.log_debug(`pkill -9 memcachedb`)
end

def start_db_slave()
  Djinn.log_debug("Starting MemcacheDB as slave")

  # Wait for the master to come up
  db_master_ip = Djinn.get_db_master_ip()
  HelperFunctions.sleep_until_port_is_open(db_master_ip, 31000)

  my_ip = my_node.private_ip
  n = @creds['replication']

  Djinn.log_debug("Starting memcachedb slave at ip #{my_ip} and replication #{n}")
  Djinn.log_debug(`rm -rf /var/appscale/memcachedb*`)
  Kernel.system "mkdir -p /var/appscale/memcachedb"
  Kernel.system "memcachedb -p #{DB_PORT} -u root -d -r -H #{DB_LOCATION} -N -R #{my_ip}:31000 -O #{db_master_ip}:31000 -S -n #{n} >> #{DB_LOCATION}/memcachedb.log 2>&1 &"
end

def stop_db_slave
  Djinn.log_debug("Removing temp files for MemcacheDB on slave box")
  Djinn.log_debug(`pkill -9 memcachedb`)
end

def backup_db
  suffix = HelperFunctions.get_random_alphanumeric
  db_backup_filename = "#{APPSCALE_HOME}/db-backup-#{suffix}.tar.gz"
  `tar -czf #{db_backup_filename} #{DB_LOCATION}`
  return db_backup_filename
end

def restore_db_from_tar
  tar = @creds['restore_from_tar']
  command = "cp #{tar} / ; cd / ; tar zxvf #{tar}"
  Djinn.log_debug("About to restore DB by running [#{command}]")
  `#{command}`
end

def restore_db_from_ebs(ebs_location)
  abort("restoring memcachedb via ebs not supported yet")
end
