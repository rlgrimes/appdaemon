import hassapi as hass
from datetime import datetime, time
import globals


#notify group notify.ios_family - where I eventually want the notification to be sent.
#globals.py
#notify = "ios_family"


#front_door_lock_notification:
#  module: lock_notification
#  class: LockNotifications
#  lock: lock.front_door
#  lockname: "frontdoor"
#  lock_name: "Front Door"
#  alexas:
#    - media_player.kitchen_echo_show
#    - media_player.downstairs_ecobee
#    - media_player.master_bath_alexa
#    - media_player.office
#  log: lock_notification_log

class LockNotifications(hass.Hass): 
	def initialize(self): 
		self.listen_event(self.door_notification, "keymaster_lock_state_changed")

	def door_notification(self, event, data, kwargs): 
		user_code = data["code_slot"] 
		user_string = data["code_slot_name"] 
		entity = data["lockname"]
		action_type = data["action_text"]

		if entity == self.args["lockname"]:
			entity_name = self.args["lock_name"]
	
			if action_type == "Keypad unlock operation":
				self.log("The %s lock was just unlocked by %s", entity_name, user_string)  
				self.call_service("alarm_control_panel/alarm_disarm", entity_id = 'alarm_control_panel.home_alarm')
				if self.get_state("group.family") == "home": 
					self.log("Somebody is home and the door unlocked so this is ok") 
					message = ("The %s lock was just unlocked by %s." , entity_name, user_string)
					speak_message = ("Welcome Home %s.", user_string)
					self.run_in(self.audio_notification, 1, speak_message = speak_message)
					self.notify(message, title="{} Lock" .format(entity))

					# This is the notification that I would like to use in the future
					# self.notify(message, title="{} Lock" .format(entity), name = globals.notify)
				else: 
					self.log("The lock was just unlocked by %s", user_string) 
					message = ("The %s lock was just unlocked by %s with nobody home, are they allowed to do this?", user_string) 
					speak_message = ("Welcome Home %s.", user_string) 
					self.run_in(self.audio_notification, 1, speak_message = speak_message)
					self.notify(message, title="{} Lock" .format(entity))
								
			elif action_type == "Keypad lock operation":
				self.log("The %s lock was just locked by keypad.", entity_name) 
				message = ("The %s was just locked by the keypad", entity_name)
				self.notify(message, title="{} Lock" .format(entity), name=globals.notify)
				self.call_service("alarm_control_panel/alarm_arm_home", entity_id = 'alarm_control_panel.home_alarm')

			elif action_type == "Manual unlock operation":
				self.log("The %s lock was just unlocked by someone", entity_name) 
				if self.get_state("group.family") == "home": 
					self.log("Somebody is home and the door manually unlocked so this is ok") 
					message = ("The %s was just manually unlocked with someone home.", entity_name) 
					self.notify(message, title="{} Lock" .format(entity))
				else: 
					self.log("The %s lock was just manually unlocked.", entity_name) 
					message = ("The %s lock was just unlocked with nobody home!", entity_name) 
					speak_message = ("Hello there, be advised that I have notified the home owners that you have unlocked the %s",entity_name) 
					self.run_in(self.audio_notification, 1, speak_message = speak_message)
					self.notify(message, title="{} Lock" .format(entity))

			elif action_type == "Manual lock operation":
				self.log("The %s lock was just manually locked.", entity_name)
				message = ("The %s was manually locked.", entity_name) 
				self.notify(message, title="{} Lock" .format(entity))

			else:
				self.log("The %s lock was just operated??" % entity_name) 
				message = ("The %s was just operated with no information?" % entity_name)   
				self.notify(message, title="{} Lock" .format(entity))

	def audio_notification(self, kwargs): 
		speak_message = kwargs["speak_message"] 

		self.call_service( 
			"notify/alexa_media", 
			data = {"type": "tts"},
			target = self.args("alexas"),
			volume_level = 0.65, 
			message = speak_message,  
		)