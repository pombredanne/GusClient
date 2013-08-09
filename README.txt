---
Easy client for connecting to GUS our internal Bug Tracking System.  If you don't work for salesforce.com,
this package won't be very useful to you.

The client acts as a wrapper for the simple_salesforce package which uses the Salesforce REST API.

Additionally, the client will persist your username and security token to make logins a bit easier.  Most
users only know their password.

Ideally you would extend the gus.Gus.Client and add methods to do what you need using simple_salesforce format:

	from gus.Gus import Client
	
	gus = Client();
	
...will attempt to log into Gus and prompt you for a username, password and security_token.  If successful,
it will persist your username and security token along with the current session token in ~/.gus_data and
use it next time.  If your session token expires, it will prompt you to log in again.

The example gus client is the BacklogClient

	from gus.Gus import BacklogClient
	gus = BacklogClient()
	buildid = gus.find_build_id('MC_185')
	work = gus.find_work('W-1749572')
	gus.mark_work_fixed(work['Id'], buildid)
	
	
