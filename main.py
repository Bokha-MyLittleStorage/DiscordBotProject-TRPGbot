import discord
from discord.ext import commands
import random
import re
import os
from dotenv import load_dotenv, find_dotenv
import threading
from flask import Flask

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'봇 로그인 성공: {bot.user}')

@bot.command(name="roll", aliases=["r"])
async def roll(ctx, dice: str = '1d100'):
    print(f'roll 받음: {dice}')
    # 정규 표현식으로 'XdY' 형식 파싱
    match = re.fullmatch(r'(\d*)d(\d+)', dice.lower())
    if not match:
        await ctx.send(f'❌ 주사위 형식이 잘못되었습니다. 예: `1d20`, `3d6`, `d100`')
        return

    count_str, sides_str = match.groups()
    count = int(count_str) if count_str else 1  # "d20"처럼 앞이 비어 있으면 1개로 처리
    sides = int(sides_str)

    if count <= 0 or sides <= 0 or count > 100:
        await ctx.send(f'❌ 주사위 개수는 1~100 사이여야 하고, 면수는 1 이상이어야 합니다.')
        return

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)
    roll_results = ', '.join(str(r) for r in rolls)

    if count == 1:
        await ctx.send(f'[roll] 🎲 {count}d{sides} 결과: {rolls[0]}')
    else:
        await ctx.send(f'[roll] 🎲 {count}d{sides} 결과: {roll_results} (총합: {total})')

@bot.command(name="check", aliases=["c"])
async def check(ctx, goal):
    print(f'check 받음: {goal}')
    goal = int(goal)
    roll = random.randint(1, 100)
    if goal > roll: 
        await ctx.send(f'[check] 🎲 {roll} < {goal} 판정 성공!')
    elif goal == roll:
        await ctx.send(f'[check] 🎲 {roll} = {goal} 판정 성공!')
    else:
        await ctx.send(f'[check] 🎲 {roll} > {goal} 판정 실패!')

@bot.command(name="checks", aliases=["cs"])
async def checks(ctx, goal, count):
    print(f'checks 받음: {goal}')
    goal = int(goal)
    count = int(count)
    rollList = [[], []]
    for _ in range(count):
        roll = random.randint(1, 100)
        if roll <= goal:
            rollList[0].append(roll)
        else:
            rollList[1].append(roll)
    rollList[0].sort()
    rollList[1].sort()
    await ctx.send(f'[checks] 총 판정 {count}개 중 🎲 {rollList[0]} {len(rollList[0])}개 성공!  ||  🎲 {rollList[1]} {len(rollList[1])}개 실패!')

# ----------------- 1. Discord 봇 초기화 -----------------

def run_discord_bot():
    
    load_dotenv(find_dotenv())
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    bot.run(BOT_TOKEN)

# ----------------- 2. Render용 HTTP 서버 추가 -----------------

# Render가 요구하는 PORT 환경 변수를 가져옵니다. 기본값은 10000입니다.
PORT = int(os.environ.get("PORT", 10000)) 

app = Flask(__name__)

# Render는 이 엔드포인트에 주기적으로 요청을 보내 서비스 상태를 확인합니다.
@app.route('/')
def home():
    return "Discord Bot is Running!", 200

def run_flask_server():
    # 0.0.0.0 호스트와 Render가 요구하는 PORT에 바인딩합니다.
    app.run(host='0.0.0.0', port=PORT)

# ----------------- 3. 메인 실행 -----------------

if __name__ == '__main__':
    # 봇을 별도의 스레드로 실행하여 봇과 서버가 동시에 돌아가도록 합니다.
    # Flask 서버는 메인 스레드에서 실행됩니다.
    bot_thread = threading.Thread(target=run_discord_bot)
    bot_thread.start()

    # Flask 서버 (HTTP 서버)를 시작하여 Render의 포트 바인딩 요구 사항을 충족합니다.
    run_flask_server()
