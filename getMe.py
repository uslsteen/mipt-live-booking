import asyncio
import telegram


async def main():
    bot = telegram.Bot("8184651529:AAG4ULgtyS6kwsKo1Fg1-l9O378hn7SXJTI")
    async with bot:
        print(await bot.get_me())


if __name__ == '__main__':
    asyncio.run(main())
