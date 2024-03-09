import time

from discord import VoiceState

import database
from activity.activityDb import add_points_overall, add_points_weekly
from activity.lbview import Leaderboard
from activity.pointscalc import get_required_points
from activity.process import process_message
from commandset import CommandSetManager


class ActivityManager(CommandSetManager):
    def __init__(self, client):
        super().__init__(client, ["lb", "leaderboard", "info", "p"])

    async def on_message(self, message):
        process_message(message)
        if self.is_my_message(message):
            command = message.content.split()[1]
            if command in ["leaderboard", "lb"]:
                lb = Leaderboard(self.server, self.client)
                msg = await message.channel.send("Loading...", view=lb)
                lb.message = msg
                await lb.update()

    def check_valid_vc(self, channel):
        unmuted = 0
        people = 0
        for member in channel.members:
            if not member.bot:
                people += 1
                if not (member.voice.mute or member.voice.self_mute):
                    unmuted += 1

        return people >= 2 and unmuted >= 1

    async def on_voice_state_update(self, member, before: VoiceState, after: VoiceState):
        if not database.activity.has_data(id=member.id):
            database.activity.add_data({"id":member.id, "activity":3, "progress":0})

        if not database.weekActivity.has_data(id=member.id):
            database.weekActivity.add_data({"id":member.id, "activity":3, "progress":0})
        try:
            if after.channel is None and not before.channel is None:
                if database.activityData.has_data(fId="voiceStart", id=member.id):
                    elapsed = time.time() - database.activityData.find_one(fId="voiceStart", id=member.id)["time"]
                    database.activityData.delete_data(fId="voiceStart", id=member.id)
                    add_points_overall(member.id, 3 * elapsed/3600)
                    add_points_weekly(member.id, 3 * elapsed/3600)
                    # print(f"{member.display_name} removed")

                if not self.check_valid_vc(before.channel):
                    for vcMember in before.channel.members:
                        if database.activityData.has_data(fId="voiceStart", id=vcMember.id):
                            elapsed = time.time() - database.activityData.find_one(fId="voiceStart", id=vcMember.id)["time"]
                            database.activityData.delete_data(fId="voiceStart", id=vcMember.id)
                            add_points_overall(vcMember.id, 3 * elapsed/3600)
                            add_points_weekly(vcMember.id, 3 * elapsed/3600)
                            #  print(f"{vcMember.display_name} removed")


            else:
                if after.channel is not None and before.channel is None:
                    if self.check_valid_vc(after.channel):
                        for vcMember in after.channel.members:
                            if not database.activityData.has_data(fId="voiceStart", id=vcMember.id):
                                database.activityData.add_data({"fId":"voiceStart", "id":vcMember.id, "time":time.time()})
                                # print(f"{vcMember.display_name} added")

                elif after.channel is not None and before.channel is not None:
                    if self.check_valid_vc(after.channel):
                        for vcMember in after.channel.members:
                            if not database.activityData.has_data(fId="voiceStart", id=vcMember.id):
                                database.activityData.add_data({"fId":"voiceStart", "id":vcMember.id, "time":time.time()})
                                # print(f"{vcMember.display_name} added")

                    else:
                        if database.activityData.has_data(fId="voiceStart", id=member.id):
                            elapsed = time.time() - database.activityData.find_one(fId="voiceStart", id=member.id)["time"]
                            database.activityData.delete_data(fId="voiceStart", id=member.id)
                            add_points_overall(member.id, 3 * elapsed/3600)
                            add_points_weekly(member.id, 3 * elapsed/3600)
                            # print(f"{member.display_name} removed")

                    if not self.check_valid_vc(before.channel):
                        for vcMember in before.channel.members:
                            if database.activityData.has_data(fId="voiceStart", id=vcMember.id):
                                elapsed = time.time() - database.activityData.find_one(fId="voiceStart", id=vcMember.id)["time"]
                                database.activityData.delete_data(fId="voiceStart", id=vcMember.id)
                                add_points_overall(vcMember.id, 3 * elapsed/3600)
                                add_points_weekly(vcMember.id, 3 * elapsed/3600)
                                # print(f"{vcMember.display_name} removed")

            if (after.mute or after.self_mute) and not (before.mute or after.self_mute):
                if database.activityData.has_data(fId="voiceStart", id=member.id):
                    elapsed = time.time() - database.activityData.find_one(fId="voiceStart", id=member.id)["time"]
                    database.activityData.delete_data(fId="voiceStart", id=member.id)
                    add_points_overall(member.id, 3 * elapsed/3600)
                    add_points_weekly(member.id, 3 * elapsed/3600)
                    # print(f"{member.display_name} removed")

                if not self.check_valid_vc(after.channel):
                    for vcMember in before.channel.members:
                        if database.activityData.has_data(fId="voiceStart", id=vcMember.id):
                            elapsed = time.time() - database.activityData.find_one(fId="voiceStart", id=vcMember.id)["time"]
                            database.activityData.delete_data(fId="voiceStart", id=vcMember.id)
                            add_points_overall(vcMember.id, 3 * elapsed/3600)
                            add_points_weekly(vcMember.id, 3 * elapsed/3600)
                            # print(f"{vcMember.display_name} removed")

            else:
                if not (after.mute or after.self_mute) and (before.mute or after.self_mute):
                    if self.check_valid_vc(after.channel):
                        for vcMember in before.channel.members:
                            if not database.activityData.has_data(fId="voiceStart", id=vcMember.id):
                                database.activityData.add_data({"fId":"voiceStart", "id":vcMember.id, "time":time.time()})
                                # print(f"{vcMember.display_name} added")

        except Exception as e:
            print(e)
