import discord
from discord.ext import commands
import os
import google.generativeai as genai
import asyncio
from collections import defaultdict
from datetime import datetime
import logging
import sys

try:
    from keep_alive import keep_alive
    KEEP_ALIVE_AVAILABLE = True
except ImportError:
    KEEP_ALIVE_AVAILABLE = False
    logger = logging.getLogger('discord_bot')
    logger.info("keep_alive غير متوفر - البوت سيعمل بدون Flask")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('discord_bot')

api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    logger.warning("تحذير: GOOGLE_API_KEY غير موجود")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

conversation_history = defaultdict(list)
bot_responses = defaultdict(set)
MAX_HISTORY = 15

active_tagtag = {}
channel_personality = defaultdict(lambda: "سعودي")

PERSONALITIES = {
    "سعودي": """أنت شخص سعودي طقاق ومسوّلف من أهل الرياض. تكلم بشكل طبيعي تماماً كأنك إنسان حقيقي.

قواعد الطقطقة:
- استخدم اللهجة السعودية النجدية بشكل طبيعي (مثل: وش الأخبار، كيفك، يا رجال، ولا يهمك، زين، يا ليت، إلخ)
- كن ذكي وسريع البديهة في الردود
- استخدم التورية والنكات الذكية والمواقف المضحكة
- رد بطريقة مرحة وخفيفة ظل لكن ذكية
- كن مباشر وصريح بطريقة مرحة
- لا تستخدم الإيموجي إلا نادراً جداً
- ردودك قصيرة ومركزة (1-3 جمل عادة)
- اقرأ المحادثة السابقة كلها قبل الرد عشان تفهم السياق
- لا تكرر نفسك أبداً - كل رد يكون جديد ومختلف
- تفاعل مع النقاط المهمة في المحادثة
- كن عفوي وطبيعي - لا تظهر إنك بوت
- استخدم أسلوب الطقطقة السعودية: الذكاء السريع والرد الحاضر
- اذا حد قال شي غريب أو مضحك، ارد عليه بطريقة طقاقة
- ما تقول أشياء مثل "كيف أقدر أساعدك" - أنت صديق عادي مو خدمة عملاء
""",
    
    "عراقي": """أنت شخص عراقي طقاق ومسوّلف من أهل بغداد. تكلم بشكل طبيعي تماماً كأنك إنسان حقيقي.

قواعد الطقطقة:
- استخدم اللهجة العراقية بشكل طبيعي (مثل: شلونك، شكو ماكو، ها الشباب، يا زلمة، وين رايح، شدسوي، إلخ)
- كن ذكي وسريع البديهة في الردود
- استخدم التورية والنكات العراقية الذكية
- رد بطريقة مرحة وخفيفة ظل لكن ذكية
- كن مباشر وصريح بطريقة مرحة
- لا تستخدم الإيموجي إلا نادراً جداً
- ردودك قصيرة ومركزة (1-3 جمل عادة)
- استخدم أسلوب الطقطقة العراقية: الذكاء السريع والرد الحاضر
- كن عفوي وطبيعي - لا تظهر إنك بوت
""",
    
    "سوري": """أنت شخص سوري طقاق ومسوّلف من أهل دمشق. تكلم بشكل طبيعي تماماً كأنك إنسان حقيقي.

قواعد الطقطقة:
- استخدم اللهجة الشامية بشكل طبيعي (مثل: كيفك، شو أخبارك، يا زلمة، هيدا، هيك، مبسوط، يلا، إلخ)
- كن ذكي وسريع البديهة في الردود
- استخدم التورية والنكات الشامية الذكية
- رد بطريقة مرحة وخفيفة ظل لكن ذكية
- كن مباشر وصريح بطريقة مرحة
- لا تستخدم الإيموجي إلا نادراً جداً
- ردودك قصيرة ومركزة (1-3 جمل عادة)
- كن عفوي وطبيعي - لا تظهر إنك بوت
""",
    
    "مطوع": """أنت شيخ مطوّع حكيم ومحترم. تكلم بشكل هادئ ووقور مع الحكمة والموعظة الحسنة.

قواعد الكلام:
- استخدم لغة فصيحة مع بعض العامية المهذبة
- ابدأ الكلام بـ "بارك الله فيك" أو "الله يهديك" أو عبارات دينية
- أعط نصائح حكيمة ومواعظ
- استخدم آيات قرآنية وأحاديث نبوية (بدون تفاصيل دقيقة)
- كن هادئ ووقور في ردودك
- لا تستخدم الإيموجي أبداً
- ذكّر بالله والدين بطريقة لطيفة
- ردودك حكيمة ومختصرة
""",
    
    "سكران": """أنت شخص سكران ومخمور ومو عارف وين هو. تكلم بطريقة مضحكة وغير منطقية.

قواعد الكلام:
- كلامك غير واضح ومتقطع (مثل: هااا؟ وييين؟ شششبيك؟)
- تكرر بعض الحروف والكلمات
- أفكارك مشوشة وغير منطقية
- تنسى شو كنت تقول
- تضحك بدون سبب "هههههه"
- كلامك قصير جداً ومو مفهوم
- تخلط بين المواضيع بشكل مضحك
- لا تستخدم الإيموجي
- كن مضحك بطريقة عفوية
"""
}

async def get_conversation_context(channel_id, limit=MAX_HISTORY):
    history = conversation_history[channel_id]
    return history[-limit:] if len(history) > limit else history

async def add_to_history(channel_id, role, content, message_id=None):
    conversation_history[channel_id].append({
        "role": role,
        "content": content,
        "message_id": message_id,
        "timestamp": datetime.now()
    })
    if len(conversation_history[channel_id]) > 20:
        conversation_history[channel_id] = conversation_history[channel_id][-20:]

def detect_personality_change(message_text):
    """اكتشاف تغيير اللهجة من الرسالة"""
    message_lower = message_text.lower()
    
    if any(word in message_lower for word in ["تكلم عراقي", "كلم عراقي", "صير عراقي"]):
        return "عراقي"
    elif any(word in message_lower for word in ["تكلم سوري", "كلم سوري", "صير سوري", "تكلم شامي"]):
        return "سوري"
    elif any(word in message_lower for word in ["تكلم سعودي", "كلم سعودي", "صير سعودي", "ارجع عادي"]):
        return "سعودي"
    
    return None

async def generate_response_with_retry(channel_id, user_message, max_retries=3):
    """توليد رد مع إعادة المحاولة التلقائية"""
    for attempt in range(max_retries):
        try:
            history = await get_conversation_context(channel_id)
            
            personality = channel_personality[channel_id]
            system_prompt = PERSONALITIES.get(personality, PERSONALITIES["سعودي"])
            
            messages = [system_prompt]
            for msg in history:
                messages.append(f"{msg['role']}: {msg['content']}")
            messages.append(f"user: {user_message}")
            
            model = genai.GenerativeModel(
                "gemini-2.0-flash-exp",
                generation_config={
                    "temperature": 1.2,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 500,
                }
            )
            
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, "\n".join(messages)),
                timeout=30.0
            )
            
            if response and response.text:
                logger.info(f"✅ تم توليد رد بنجاح (محاولة {attempt + 1})")
                return response.text.strip()
            else:
                logger.warning(f"⚠️ الرد فاضي من Gemini (محاولة {attempt + 1})")
                
        except asyncio.TimeoutError:
            logger.error(f"⏱️ انتهى الوقت في المحاولة {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
        except Exception as e:
            logger.error(f"❌ خطأ في المحاولة {attempt + 1}: {type(e).__name__} - {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 * (attempt + 1))
    
    return None

@bot.event
async def on_ready():
    if bot.user:
        logger.info(f'🤖 البوت جاهز! مسجل الدخول باسم {bot.user.name}')
        logger.info(f'🆔 ID: {bot.user.id}')
        logger.info('─' * 50)

@bot.event
async def on_command_error(ctx, error):
    """معالجة أخطاء الأوامر"""
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("ما لقيت هالشخص، تأكد من الاسم")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"ناقص معلومة: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        logger.error(f"خطأ في الأمر: {type(error).__name__} - {str(error)}")
        await ctx.send("صار خطأ في تنفيذ الأمر، جرب مرة ثانية")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('.'):
        await bot.process_commands(message)
        return

    channel_id = message.channel.id

    should_reply_tagtag = False
    if channel_id in active_tagtag:
        tagtag_config = active_tagtag[channel_id]
        if tagtag_config['is_everyone']:
            should_reply_tagtag = True
        elif tagtag_config['target_user_id'] == message.author.id:
            should_reply_tagtag = True

    bot_mentioned = bot.user.mentioned_in(message) if bot.user else False
    is_reply_to_bot = False
    if message.reference:
        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            is_reply_to_bot = replied_message.author == bot.user
        except:
            pass

    if bot_mentioned or is_reply_to_bot or should_reply_tagtag:
        user_id_mention = f'<@{bot.user.id}>' if bot.user else ''
        clean_message = message.content.replace(user_id_mention, '').strip()
        
        personality_change = detect_personality_change(clean_message)
        if personality_change:
            channel_personality[channel_id] = personality_change
            personality_names = {
                "سعودي": "السعودية",
                "عراقي": "العراقية",
                "سوري": "السورية"
            }
            await message.channel.send(f"تمام! الحين راح أكلم باللهجة {personality_names.get(personality_change, personality_change)} 👌")
        
        await add_to_history(channel_id, "user", clean_message, message.id)

        async with message.channel.typing():
            response = await generate_response_with_retry(channel_id, clean_message)

            if response:
                recent_responses = [
                    msg["content"] for msg in conversation_history[channel_id] 
                    if msg["role"] == "assistant"
                ][-10:]
                
                if response not in recent_responses:
                    try:
                        sent_message = await message.channel.send(response)
                        await add_to_history(channel_id, "assistant", response, sent_message.id)
                        bot_responses[channel_id].add(sent_message.id)
                    except discord.Forbidden:
                        logger.error("❌ ما عندي صلاحية للإرسال في هالقناة")
                    except discord.HTTPException as e:
                        logger.error(f"❌ خطأ في إرسال الرسالة: {e}")
                        await message.add_reaction("❌")
                else:
                    await message.channel.send("قلها بطريقة ثانية عشان أفهم أحسن")
            else:
                error_messages = [
                    "يا زلمة صار خطأ، جرب مرة ثانية",
                    "الخدمة مشغولة شوية، جرب بعد شوي",
                    "ما قدرت أجاوب هالمرة، حاول مرة ثانية"
                ]
                import random
                await message.channel.send(random.choice(error_messages))

@bot.command(name='مسح')
async def clear_history(ctx):
    """مسح سياق المحادثة"""
    channel_id = ctx.channel.id
    conversation_history[channel_id] = []
    bot_responses[channel_id] = set()
    await ctx.send("تم! مسحت كل شي ونبدأ من جديد 🔄")

@bot.command(name='حالة')
async def status(ctx):
    """عرض حالة البوت"""
    channel_id = ctx.channel.id
    history_count = len(conversation_history.get(channel_id, []))
    await ctx.send(f"✅ البوت شغال تمام\n💬 عدد الرسائل بالذاكرة: {history_count}")

@bot.command(name='طقطق')
async def tagtag(ctx, member: discord.Member):
    """تفعيل الطقطقة على شخص معين"""
    channel_id = ctx.channel.id
    active_tagtag[channel_id] = {
        'target_user_id': member.id,
        'is_everyone': False
    }
    await ctx.send(f"يلا بينا! فعّلت الطقطقة على {member.mention} 🎯")

@bot.command(name='طقطق_الكل')
async def tagtag_everyone(ctx):
    """تفعيل الطقطقة على الجميع"""
    channel_id = ctx.channel.id
    active_tagtag[channel_id] = {
        'target_user_id': None,
        'is_everyone': True
    }
    await ctx.send("يلا! الطقطقة على الكل الحين 🔥")

@bot.command(name='وقف')
async def stop_tagtag(ctx):
    """إيقاف الطقطقة"""
    channel_id = ctx.channel.id
    if channel_id in active_tagtag:
        del active_tagtag[channel_id]
        await ctx.send("تمام، وقفت الطقطقة ✋")
    else:
        await ctx.send("ما فيه طقطقة شغالة أصلاً")

@bot.command(name='فحص')
async def check_bot(ctx):
    """فحص حالة البوت"""
    channel_id = ctx.channel.id
    ping = round(bot.latency * 1000)
    history_count = len(conversation_history.get(channel_id, []))

    tagtag_status = "غير مفعلة"
    if channel_id in active_tagtag:
        if active_tagtag[channel_id]['is_everyone']:
            tagtag_status = "مفعلة على الجميع 🔥"
        else:
            user_id = active_tagtag[channel_id]['target_user_id']
            tagtag_status = f"مفعلة على <@{user_id}> 🎯"

    embed = discord.Embed(title="🤖 فحص البوت", color=0x00ff00)
    embed.add_field(name="📶 البنق", value=f"{ping}ms", inline=True)
    embed.add_field(name="💬 الرسائل في الذاكرة", value=str(history_count), inline=True)
    embed.add_field(name="🎯 حالة الطقطقة", value=tagtag_status, inline=False)

    await ctx.send(embed=embed)

@bot.command(name='مساعدة', aliases=['اوامر'])
async def help_command(ctx):
    """عرض الأوامر المتاحة"""
    help_text = """
**🎯 أوامر البوت:**

**الطقطقة:**
• `.طقطق @شخص` - تفعيل الطقطقة على شخص معين
• `.طقطق_الكل` - تفعيل الطقطقة على الجميع
• `.وقف` - إيقاف الطقطقة

**إدارة المحادثة:**
• `.مسح` - مسح سياق المحادثة
• `.حالة` - عرض حالة البوت
• `.فحص` - فحص تفصيلي للبوت

**طريقة الاستخدام:**
- امنشن البوت أو رد على رسالته عشان يرد عليك
- أو فعّل الطقطقة وخله يرد على كل شي!
"""
    await ctx.send(help_text)

if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.error("❌ خطأ: لم يتم العثور على DISCORD_TOKEN")
        sys.exit(1)
    else:
        if KEEP_ALIVE_AVAILABLE:
            keep_alive()
            logger.info("✅ Flask server شغال للحفاظ على البوت نشط")
        
        logger.info("🚀 بدء تشغيل البوت...")
        try:
            bot.run(token, log_handler=None)
        except discord.LoginFailure:
            logger.error("❌ فشل تسجيل الدخول - تأكد من صحة التوكن")
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
