from redbot.core.i18n import Translator
from redbot.core.utils import chat_formatting as cf, predicates

import trainerdex

_ = Translator("TrainerDex", __file__)


def check_xp(x: trainerdex.Update) -> int:
    if x.xp is None:
        return 0
    return x.xp


def contact_us_on_twitter() -> str:
    return cf.info(
        _("If that doesn't look right, please contact us on Twitter. {twitter_handle}")
    ).format(twitter_handle="@TrainerDexApp")


def append_twitter(text: str) -> str:
    return "{original_message}\n\n{twitter}".format(
        original_message=text, twitter=contact_us_on_twitter()
    )


def loading(text: str) -> str:
    """Get text prefixed with a loading emoji if the bot has access to it.

    Returns
    -------
    str
    The new message.

    """

    emoji = "<a:loading:471298325904359434>"
    return f"{emoji} {text}"


def success(text: str) -> str:
    """Get text prefixed with a white checkmark.

    Returns
    -------
    str
    The new message.

    """
    emoji = "\N{WHITE HEAVY CHECK MARK}"
    return f"{emoji} {text}"


class QuestionMessage:
    def __init__(self, ctx, question: str, check=None):
        self._ctx = ctx
        self.question = question
        self.message = None
        if check:
            self.predicate = check
        else:
            self.predicate = predicates.MessagePredicate.same_context(self._ctx)
        self.response = None

    async def ask(self, bot):
        self.message = await self._ctx.send(
            cf.question(f"{self._ctx.author.mention}: {self.question}")
        )
        self.response = await bot.wait_for("message", check=self.predicate)

    @property
    def answer(self) -> str:
        if self.response:
            return self.response.content
        return None

    @property
    def exit(self) -> bool:
        if self.answer:
            return self.answer.lower() == f"{self._ctx.prefix}cancel"
        return False
