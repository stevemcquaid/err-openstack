from errbot import BotPlugin, botcmd

class HelloWorld(BotPlugin):
    @botcmd                               # this tag this method as a command
    def hello(self, mess, args):          # it will respond to !hello
        """ this command says hello """   # this will be the answer of !help hello
        return 'Hello World !'            # the bot will answer that

    def callback_message(self, mess):
        if str(mess).find('cookie') != -1:
            self.send(mess.getFrom(), "What what somebody said cookie !?", message_type=mess.getType())
