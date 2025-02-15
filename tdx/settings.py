import json
import logging
from discord.ext.alternatives import silent_delete
from discord.message import Message
from discord.role import Role
from redbot.core import checks, commands
from redbot.core.commands.converter import Literal
from redbot.core.i18n import Translator
from redbot.core.utils import chat_formatting as cf
from typing import Dict, Optional

from .abc import MixinMeta
from .datatypes import ChannelConfig, GuildConfig, StoredRoles

logger: logging.Logger = logging.getLogger(__name__)
_ = Translator("TrainerDex", __file__)


class Settings(MixinMeta):
    @commands.command(name="quickstart")
    @checks.mod_or_permissions(manage_guild=True)
    @checks.bot_in_a_guild()
    async def quickstart(self, ctx: commands.Context) -> None:
        await ctx.tick()
        message: Message = await ctx.send(_("Looking for team roles…"))

        try:
            mystic_role: Role = min(
                [x for x in ctx.guild.roles if _("Mystic").casefold() in x.name.casefold()]
            )
        except ValueError:
            mystic_role = None
        if mystic_role:
            await self.config.guild(ctx.guild).mystic_role.set(mystic_role.id)
            await ctx.send(
                _("`{key}` set to {value}").format(key="mystic_role", value=mystic_role),
                delete_after=30,
            )

        try:
            valor_role: Role = min(
                [x for x in ctx.guild.roles if _("Valor").casefold() in x.name.casefold()]
            )
        except ValueError:
            valor_role = None
        if valor_role:
            await self.config.guild(ctx.guild).valor_role.set(valor_role.id)
            await ctx.send(
                _("`{key}` set to {value}").format(key="valor_role", value=valor_role),
                delete_after=30,
            )

        try:
            instinct_role: Role = min(
                [x for x in ctx.guild.roles if _("Instinct").casefold() in x.name.casefold()]
            )
        except ValueError:
            instinct_role = None
        if instinct_role:
            await self.config.guild(ctx.guild).instinct_role.set(instinct_role.id)
            await ctx.send(
                _("`{key}` set to {value}").format(key="instinct_role", value=instinct_role),
                delete_after=30,
            )

        await message.edit(content=_("Looking for TL40 role…"))

        try:
            tl40_role: Role = min(
                [
                    x
                    for x in ctx.guild.roles
                    if (_("Level 40").casefold() in x.name.casefold())
                    or ("tl40".casefold() in x.name.casefold())
                ]
            )
        except ValueError:
            tl40_role = None
        if tl40_role:
            await self.config.guild(ctx.guild).tl40_role.set(tl40_role.id)
            await ctx.send(
                _("`{key}` set to {value}").format(key="tl40_role", value=tl40_role),
                delete_after=30,
            )

        await message.delete(silent=True)

        guild_config: GuildConfig = GuildConfig(**(await self.config.guild(ctx.guild).all()))
        output: str = json.dumps(guild_config.__dict__, indent=2, ensure_ascii=False)
        await ctx.send(cf.box(output, "json"))

    @commands.group(name="tdxset", aliases=["config"], case_insensitive=True)
    async def tdxset(self, ctx: commands.Context) -> None:
        """⬎ Set server and/or channel settings"""
        pass

    @tdxset.group(name="guild", aliases=["server"], case_insensitive=True)
    @checks.mod_or_permissions(manage_guild=True)
    @checks.bot_in_a_guild()
    async def tdxset__guild(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            guild_config: GuildConfig = GuildConfig(**(await self.config.guild(ctx.guild).all()))
            output: str = json.dumps(guild_config.__dict__, indent=2, ensure_ascii=False)
            await ctx.send(cf.box(output, "json"))

    @tdxset__guild.command(name="assign_roles_on_join")
    async def tdxset__guild__assign_roles_on_join(
        self, ctx: commands.Context, value: Optional[bool] = None
    ) -> None:
        """Modify the roles of members when they're approved.

        This is useful for granting users access to the rest of the server.
        """
        if value is not None:
            await self.config.guild(ctx.guild).assign_roles_on_join.set(value)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="guild.assign_roles_on_join", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: bool = await self.config.guild(ctx.guild).assign_roles_on_join()
            await ctx.send(
                _("`{key}` is {value}").format(key="guild.assign_roles_on_join", value=value)
            )

    @tdxset__guild.command(name="set_nickname_on_join")
    async def tdxset__guild__set_nickname_on_join(
        self, ctx: commands.Context, value: Optional[bool] = None
    ) -> None:
        """Modify the nickname of members when they're approved.

        This is useful for ensuring players can be easily identified.
        """
        if value is not None:
            await self.config.guild(ctx.guild).set_nickname_on_join.set(value)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="guild.set_nickname_on_join", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: bool = await self.config.guild(ctx.guild).set_nickname_on_join()
            await ctx.send(
                _("`{key}` is {value}").format(key="guild.set_nickname_on_join", value=value)
            )

    @tdxset__guild.command(name="set_nickname_on_update")
    async def tdxset__guild__set_nickname_on_update(
        self, ctx: commands.Context, value: Optional[bool] = None
    ) -> None:
        """Modify the nickname of members when they update their Total XP.

        This is useful for setting levels in their name.
        """
        if value is not None:
            await self.config.guild(ctx.guild).set_nickname_on_update.set(value)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(
                    key="guild.set_nickname_on_update", value=value
                ),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: bool = await self.config.guild(ctx.guild).set_nickname_on_update()
            await ctx.send(
                _("`{key}` is {value}").format(key="guild.set_nickname_on_update", value=value)
            )

    @tdxset__guild.command(name="roles_to_assign_on_approval")
    async def tdxset__guild__roles_to_assign_on_approval(
        self,
        ctx: commands.Context,
        action: Optional[Literal["add", "remove"]] = None,
        roles: Optional[Role] = None,
    ) -> None:
        """Which roles to add/remove to a user on approval

        Usage:
            [p]tdxset guild roles_to_assign_on_approval add @Verified, @Trainer ...
                Assign these roles to users when they are approved
            [p]tdxset guild roles_to_assign_on_approval remove @Guest
                Remove these roles from users when they are approved
        """
        stored_roles: StoredRoles = await self.config.guild(
            ctx.guild
        ).roles_to_assign_on_approval()

        if action == "add":
            if roles:
                stored_roles["add"] = [x.id for x in ctx.message.role_mentions]
                await self.config.guild(ctx.guild).roles_to_assign_on_approval.set(stored_roles)
                await ctx.tick()
                stored_roles: StoredRoles = await self.config.guild(
                    ctx.guild
                ).roles_to_assign_on_approval()
                stored_roles_json: str = json.dumps(stored_roles, indent=2, ensure_ascii=False)
                await ctx.send(cf.box(stored_roles_json, "json"), delete_after=30)
        elif action == "remove":
            if roles:
                stored_roles["remove"] = [x.id for x in ctx.message.role_mentions]
                await self.config.guild(ctx.guild).roles_to_assign_on_approval.set(stored_roles)
                await ctx.tick()
                stored_roles: StoredRoles = await self.config.guild(
                    ctx.guild
                ).roles_to_assign_on_approval()
                stored_roles_json: str = json.dumps(stored_roles, indent=2, ensure_ascii=False)
                await ctx.send(cf.box(stored_roles_json, "json"), delete_after=30)
        else:
            await ctx.send_help()
            stored_roles_json: str = json.dumps(stored_roles, indent=2, ensure_ascii=False)
            await ctx.send(cf.box(stored_roles_json, "json"))

    @tdxset__guild.command(name="mystic_role", aliases=["mystic"])
    async def tdxset__guild__mystic_role(
        self, ctx: commands.Context, value: Optional[Role] = None
    ) -> None:
        if value is not None:
            await self.config.guild(ctx.guild).mystic_role.set(value.id)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="guild.mystic_role", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: int = await self.config.guild(ctx.guild).mystic_role()
            await ctx.send(
                _("`{key}` is {value}").format(
                    key="guild.mystic_role", value=ctx.guild.get_role(value)
                )
            )

    @tdxset__guild.command(name="valor_role", aliases=["valor"])
    async def tdxset__guild__valor_role(
        self, ctx: commands.Context, value: Optional[Role] = None
    ) -> None:
        if value is not None:
            await self.config.guild(ctx.guild).valor_role.set(value.id)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="guild.valor_role", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: int = await self.config.guild(ctx.guild).valor_role()
            await ctx.send(
                _("`{key}` is {value}").format(
                    key="guild.valor_role", value=ctx.guild.get_role(value)
                )
            )

    @tdxset__guild.command(name="instinct_role", aliases=["instinct"])
    async def tdxset__guild__instinct_role(
        self, ctx: commands.Context, value: Optional[Role] = None
    ) -> None:
        if value is not None:
            await self.config.guild(ctx.guild).instinct_role.set(value.id)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="guild.instinct_role", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: int = await self.config.guild(ctx.guild).instinct_role()
            await ctx.send(
                _("`{key}` is {value}").format(
                    key="guild.instinct_role", value=ctx.guild.get_role(value)
                )
            )

    @tdxset__guild.command(name="tl40_role", aliases=["tl40"])
    async def tdxset__guild__tl40_role(
        self, ctx: commands.Context, value: Optional[Role] = None
    ) -> None:
        if value is not None:
            await self.config.guild(ctx.guild).tl40_role.set(value.id)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="guild.tl40_role", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: int = await self.config.guild(ctx.guild).tl40_role()
            await ctx.send(
                _("`{key}` is {value}").format(
                    key="guild.tl40_role", value=ctx.guild.get_role(value)
                )
            )

    @tdxset__guild.command(name="introduction_note")
    async def tdxset__guild__introduction_note(
        self, ctx: commands.Context, value: Optional[str] = None
    ) -> None:
        """Send a note to a member upon running `profile create` (aka, `approve`)

        Set value to `None` to empty it
        """
        if value is not None:
            if value == "None":
                value = None
            await self.config.guild(ctx.guild).introduction_note.set(value)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="guild.introduction_note", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: str = await self.config.guild(ctx.guild).introduction_note()
            await ctx.send(
                _("`{key}` is {value}").format(key="guild.introduction_note", value=value)
            )

    @tdxset.group(name="channel", case_insensitive=True)
    @checks.mod_or_permissions(manage_guild=True)
    @checks.bot_in_a_guild()
    async def tdxset__channel(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            channel_config: ChannelConfig = ChannelConfig(
                **(await self.config.channel(ctx.channel).all())
            )
            output: str = json.dumps(channel_config.__dict__, indent=2, ensure_ascii=False)
            await ctx.send(cf.box(output, "json"))

    @tdxset__channel.command(name="profile_ocr", aliases=["ocr"])
    async def tdxset__channel__profile_ocr(
        self, ctx: commands.Context, value: Optional[bool] = None
    ) -> None:
        """Set if this channel should accept OCR commands."""
        if value is not None:
            await self.config.channel(ctx.channel).profile_ocr.set(value)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(
                    key=f"channel[{ctx.channel.id}].profile_ocr", value=value
                ),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: bool = await self.config.channel(ctx.channel).profile_ocr()
            await ctx.send(
                _("`{key}` is {value}").format(
                    key=f"channel[{ctx.channel.id}].profile_ocr", value=value
                )
            )

    @tdxset.command(name="notice")
    @checks.is_owner()
    async def tdxset__notice(self, ctx: commands.Context, value: Optional[str] = None) -> None:
        if value is not None:
            if value == "None":
                value = None
            await self.config.notice.set(value)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="notice", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: str = await self.config.notice()
            await ctx.send(_("`{key}` is {value}").format(key="notice", value=value))

    @tdxset.command(name="footer")
    @checks.is_owner()
    async def tdxset__footer(self, ctx: commands.Context, value: Optional[str] = None) -> None:
        if value is not None:
            if value == "None":
                value = None
            await self.config.embed_footer.set(value)
            await ctx.tick()
            await ctx.send(
                _("`{key}` set to {value}").format(key="embed_footer", value=value),
                delete_after=30,
            )
        else:
            await ctx.send_help()
            value: str = await self.config.embed_footer()
            await ctx.send(_("`{key}` is {value}").format(key="embed_footer", value=value))
