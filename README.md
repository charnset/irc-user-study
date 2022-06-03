# irc-user-study
This is Fork Library of Jeffrey Liu - USC/ISI Work

The three files about configuration of IRC Server and KiwiIRC are 1)IRC_Server_config.conf 2)KiwiIRC_client.json 3)KiwiIRC_config.conf

For IRC_Server_config.conf:

IRC_Server_config.conf -> Changes:

1. Bind the address to the IRC server address
<bind address="128.9.36.31"
    port="6697"
    type="clients">
2. Set the oper(operator) and admin related information 
  <oper name="Pithayuth Charnsethikul"
    password=""
    host="*@128.9.36.31"
    type="NetAdmin">
    
  <admin name="Jeffrey Liu"
       nick="JL"
       email="jeffreyl@isi.edu">
3. Settings for the main server
    
  <server name="irc.user_study.com"
        description="IRC Server with Puppeteer Chat Bot"
        network="irc.user_study.com"
        id="77A">

For KiwiIRC_client.json:
    1. Change the kiwi server address to match our main server address
      """
      ["kiwiServer": "128.9.36.31",]
      """
    2. Set the default IRC server the client will connect to.
      """
      "startupOptions" : {
                "server": "128.9.36.31",
      """
 For KiwiIRC_config.conf:
    1. Set the upstream server as our main server
    """
    [upstream.1]
    hostname = "128.9.36.31"
    post = 6697
    """
    2. Set the HTTP server's port as 8080 instead of the default value (80) to avoid flood of spam
    """ 
    [server.1]
    bind = "0.0.0.0"
    port = 8080
    """
    
