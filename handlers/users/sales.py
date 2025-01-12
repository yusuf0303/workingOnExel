import mysql.connector
from aiogram import types
from loader import dp, bot
import datetime
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from states.contractor_states import CONTRACTOR
from handlers.users.admin import in_list
from handlers.users.admin import get_db_connection

def get_today():
    return datetime.datetime.today().date()


@dp.message_handler(Text(equals="Savdo kiritishni boshlash"), state=CONTRACTOR.start_menu)
async def all_sales(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select name from users where telegram_id = %s", (message.from_user.id,))
    name = cursor.fetchone()
    
    await message.answer(f"<strong>{get_today()} | {name[0]}\n\n1. Olingan buyurtmalar soni:</strong> [ Kiriting ]")
    await CONTRACTOR.all_sales.set()


@dp.message_handler(state=CONTRACTOR.all_sales, regexp=r"^\d+$")
async def handle_all_sales(message: types.Message, state: FSMContext):
    async with state.proxy() as adding_sales:
        adding_sales['all_sales'] = message.text
    await message.answer(f"<strong>{get_today()}</strong>\n\n"
                         f"<strong>1. Olingan buyurtmalar soni:</strong> [ {message.text} ]\n"
                         f"<strong>2. Shartnoma qilinganlar soni:</strong> [ Kiriting ]")
    await CONTRACTOR.made_contract.set()


# def cause_of_contracts(cause_contract):
#     temp = []
#     temp.append(cause_contract)


@dp.message_handler(state=CONTRACTOR.made_contract, regexp=r"^\d+$")
async def handle_made_contract(message: types.Message, state: FSMContext):
    made_contract = int(message.text)

    # Check if the input is a valid number of contracts made
    if made_contract < 0:
        await message.answer("Shartnoma qilinganlar soni 0 yoki undan katta bo'lishi kerak. Iltimos, qaytadan kiriting.")
        return
    elif made_contract == 0:
        # Store the number of contracts made and calculate contracts not made
        data['made_contract'] = made_contract
        not_made_contracts = all_sales - made_contract
        data['not_made_contract'] = not_made_contracts

        # Prepare the initial response text
        text_msg = (
            f"<strong>{get_today()}</strong>\n\n"
            f"<strong>1. Olingan buyurtmalar soni:</strong> [ {all_sales} ]\n"
            f"<strong>2. Shartnoma qilinganlar soni:</strong> [ {made_contract} ]\n"
            f"<strong>3. Shartnoma qilinmaganlar soni:</strong> [ {not_made_contracts} ]"
        )
        data["text_message_part_two"] = text_msg

        # Send the initial message
        await message.answer(text_msg, parse_mode="HTML")

        # Initialize the reason counter for collecting reasons
        await state.update_data(reason_counter_not_made=0)

        # Prompt the user to enter the first reason for contracts made
        await message.answer("<strong>Shartnoma qilinmaganlik sababi [ 1 ] ni kiriting:</strong>", parse_mode="HTML")
        await CONTRACTOR.collect_reasons_not_made.set()
    else:
        async with state.proxy() as data:
            # Retrieve the total number of sales
            all_sales = int(data.get("all_sales", 0))

            # Validate made_contract against all_sales
            if made_contract > all_sales:
                await message.answer(
                    f"Shartnoma qilinganlar soni umumiy buyurtma sonidan oshib ketmasligi kerak. "
                    f"Olingan buyurtmalar soni: [ {all_sales} ]. Iltimos, qaytadan kiriting."
                )
                return

            # Store the number of contracts made and calculate contracts not made
            data['made_contract'] = made_contract
            not_made_contracts = all_sales - made_contract
            data['not_made_contract'] = not_made_contracts

            # Prepare the initial response text
            text_msg = (
                f"<strong>{get_today()}</strong>\n\n"
                f"<strong>1. Olingan buyurtmalar soni:</strong> [ {all_sales} ]\n"
                f"<strong>2. Shartnoma qilinganlar soni:</strong> [ {made_contract} ]\n"
            )
            data["text_message_part_one"] = text_msg

        # Send the initial message
        await message.answer(text_msg, parse_mode="HTML")

        # Initialize the reason counter for collecting reasons
        await state.update_data(reason_counter=0)

        # Prompt the user to enter the first reason for contracts made
        await message.answer("<strong>Shartnoma qilinish sababi [ 1 ] ni kiriting:</strong>", parse_mode="HTML")
        await CONTRACTOR.collect_reasons.set()


@dp.message_handler(state=CONTRACTOR.collect_reasons)
async def collect_reasons(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        reason_counter = data.get("reason_counter", 0)
        made_contract = data.get("made_contract", 0)

        # Save the reason
        data[f'cause_{reason_counter}'] = message.text

        # Increment the reason counter
        reason_counter += 1
        data['reason_counter'] = reason_counter

        # Check if all reasons are collected
        if reason_counter < made_contract:
            await message.answer(f"<strong>Shartnoma qilinish sababi [ {reason_counter + 1} ] ni kiriting:</strong>",
                                 parse_mode="HTML")
        else:
            msg_part_one = data.get("text_message_part_one", 0)
            not_made_contracts = data.get('not_made_contract')
            # All reasons collected, finalize
            reasons = "\n".join(
                [f"{i + 1}. {data[f'cause_{i}']}" for i in range(made_contract)]
            )
            text_msg = (
                f"{msg_part_one}\n"
                f"<strong>Shartnoma qilinish sabablari:</strong>\n<code>{reasons}</code>\n\n"
                f"<strong>3. Shartnoma qilinmaganlar soni:</strong> [ {not_made_contracts} ]"
            )
            await message.answer(text_msg, parse_mode="HTML")
            data["text_message_part_two"] = text_msg

            # Initialize reason counter
            await state.update_data(reason_counter_not_made=0)

            # Prompt for the first reason
            await message.answer(f"<strong>Shartnoma qilinmaganlik sababi [ 1 ] ni kiriting:</strong>", parse_mode="HTML")
            await CONTRACTOR.collect_reasons_not_made.set()



@dp.message_handler(state=CONTRACTOR.collect_reasons_not_made)
async def collect_reasons_not_made(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Get the current counter for reasons not made and total contracts not made
        reason_counter_not_made = data.get("reason_counter_not_made", 0)
        not_made_contracts = data.get("not_made_contract", 0)

        # Save the reason for the current "not made" contract
        data[f'not_made_cause_{reason_counter_not_made}'] = message.text

        # Increment the reason counter
        reason_counter_not_made += 1
        data['reason_counter_not_made'] = reason_counter_not_made

        # Check if all reasons are collected
        if reason_counter_not_made < not_made_contracts:
            # Prompt for the next reason
            await message.answer(f"<strong>Shartnoma qilinmaganlik sababi [ {reason_counter_not_made + 1} ] ni kiriting:</strong>",
                                 parse_mode="HTML")
        else:
            # All reasons for "not made" contracts collected
            not_made_reasons = "\n".join(
                [f"{i + 1}. {data[f'not_made_cause_{i}']}" for i in range(not_made_contracts)]
            )
            final_summary = (
                f"{data['text_message_part_two']}\n\n"
                f"<strong>Shartnoma qilinmaganlik sabablari:</strong>\n<code>{not_made_reasons}</code>\n\n"
                f"Ma'lumotlar to'liq kiritildi. Rahmat!"
            )

            # Send the final summary
            await message.answer(final_summary, parse_mode="HTML")
            await state.finish()





    # connection = get_db_connection()
    # cursor = connection.cursor()

    # # Foydalanuvchi ma'lumotlarini olish
    # cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
    # user = cursor.fetchone()

    # # Foydalanuvchi shartnomachi bo'lsa
    # if user and user[3] == 'contractor':
    #     # Faqat raqamlarni qabul qilish
    #     if message.text.isdigit() or isinstance(float(message.text), float):
    #         sales_value = float(message.text)

    #         # Foydalanuvchi ID'sini olish
    #         cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
    #         user_id = cursor.fetchone()[0]

    #         today = datetime.date.today()

    #         # Bugungi kunda shartnomachi savdo kiritganmi tekshirish
    #         cursor.execute("SELECT * FROM daily_sales WHERE user_id = %s AND sale_date = %s", (user_id, today))
    #         existing_sale = cursor.fetchone()

    #         if existing_sale:
    #             # Agar savdo bor bo'lsa, xabar yuborish
    #             await message.reply("Bugun siz allaqachon savdo kiritdingiz. Iltimos, ertaga yana urinib ko'ring.")
    #         else:
    #             # Jami savdolarni hisoblash
    #             cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
    #             total_sales = cursor.fetchone()[0]

    #             if total_sales:
    #                 # Maqsadni olish
    #                 cursor.execute("SELECT target FROM users WHERE id = %s", (user_id,))
    #                 target = cursor.fetchone()[0]

    #                 # Reja bajarilish foizi
    #                 percent = (total_sales / target) * 100

    #                 # Savdo kiritish
    #                 cursor.execute("INSERT INTO daily_sales (user_id, sales, sale_date, percent) VALUES (%s, %s, %s, %s)",
    #                             (user_id, sales_value, today, percent))
    #                 connection.commit()
    #             else:
    #                 cursor.execute("INSERT INTO daily_sales (user_id, sales, sale_date) VALUES (%s, %s, %s)",
    #                                (user_id, sales_value, today))
    #                 connection.commit()

    #                 cursor.execute("select target from users where id = %s", (user_id,))
    #                 target = cursor.fetchone()[0]

    #                 cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
    #                 total_sales = cursor.fetchone()[0]


    #                 # cursor.execute("select percent from daily_sales where id = %s", (user_id,))
    #                 # old_percent = cursor.fetchone()

    #                 percent = (total_sales / target) * 100

    #                 cursor.execute("UPDATE daily_sales SET percent = %s WHERE user_id = %s and percent = 0.00", 
    #                                (percent, user_id))
    #                 connection.commit()

    #             # Oylik hisobotni kiritish
    #             # cursor.execute(
    #             #     "INSERT INTO monthly_reports (user_id, month, year, total_sales, percent, day) VALUES (%s, %s, "
    #             #     "%s, %s, %s, %s)",
    #             #     (user_id, today.month, today.year, total_sales, percent, today.day))
    #             # connection.commit()
    #             if percent >= 100:
    #                 # Ma'lumotlarni `monthly_reports` jadvaliga qo'shish
    #                 cursor.execute("INSERT INTO monthly_reports (user_id, month, year, total_sales, percent, "
    #                                "day) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, today.month, today.year,
    #                                                                         total_sales, percent, today.day))
    #                 connection.commit()

    #                 # `daily_sales` jadvalidan tozalash
    #                 cursor.execute("DELETE FROM daily_sales WHERE user_id = %s", (user_id,))
    #                 connection.commit()

    #                 # Yangi savdo kiritish boshlanishi haqida xabar yuborish
    #                 await message.reply(
    #                     "Reja 100% bajarildi! Yangi oy uchun savdo boshlanadi. Yangi savdolarni kiritish mumkin.")

    #             # Darajani aniqlash
    #             if total_sales < 26000:
    #                 degree = "✔️"
    #             elif 26000 <= total_sales < 52000:
    #                 degree = "☑️"
    #             else:
    #                 degree = "✅"

    #             # Joriy sana va vaqtni olish
    #             datetimes = datetime.datetime.now()
    #             date = datetimes.strftime("%Y-%m-%d")
    #             time = datetimes.strftime("%H:%M:%S")

    #             cursor.execute("SELECT name FROM users WHERE telegram_id = %s", (message.from_user.id,))
    #             name = cursor.fetchone()

    #             message_text = (f"{date} | {time}\n\n"
    #                             f"👤: {name[0]}\n🆔: {message.from_user.id}\n\n"
    #                             f"Savdo qo'shildi 💰: {sales_value}$.\n"
    #                             f"Jami savdo 💹: {total_sales}$.\nReja: {percent:.2f}% bajarildi {degree}")

    #             await message.reply(message_text)

    #             await bot.send_message(chat_id="-1002293235387", text=message_text)

    #             cursor.close()
    #             connection.close()
    #     else:
    #         await message.reply("Savdoni faqat butun va haqiqiy sonlarda kiriting!")
    # else:
    #     await message.answer("Siz shartnomachi emassiz!")


# Kerakli qismini olish kerak!

# @dp.message_handler()
# async def handle_save_sales(message: types.Message):
#     connection = get_db_connection()
#     cursor = connection.cursor()
#
#     # Foydalanuvchi ma'lumotlarini olish
#     cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (message.from_user.id,))
#     user = cursor.fetchone()
#
#     # Foydalanuvchi shartnomachi bo'lsa
#     if user and user[3] == 'contractor':
#         # Faqat raqamlarni qabul qilish
#         if message.text.isdigit() or isinstance(float(message.text), float):
#             sales_value = float(message.text)
#
#             # Foydalanuvchi ID'sini olish
#             cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (message.from_user.id,))
#             user_id = cursor.fetchone()[0]
#
#             today = datetime.date.today()
#
#             # Bugungi kunda shartnomachi savdo kiritganmi tekshirish
#             cursor.execute("SELECT * FROM daily_sales WHERE user_id = %s AND date = %s", (user_id, today))
#             existing_sale = cursor.fetchone()
#
#             if existing_sale:
#                 # Agar savdo bor bo'lsa, xabar yuborish
#                 await message.reply("Bugun siz allaqachon savdo kiritdingiz. Iltimos, ertaga yana urinib ko'ring.")
#             else:
#                 # Savdo kiritish
#                 cursor.execute("INSERT INTO daily_sales (user_id, sales, date) VALUES (%s, %s, %s)",
#                                (user_id, sales_value, today))
#                 connection.commit()
#
#                 # Jami savdolarni hisoblash
#                 cursor.execute("SELECT SUM(sales) FROM daily_sales WHERE user_id = %s", (user_id,))
#                 total_sales = cursor.fetchone()[0]
#
#                 # Maqsadni olish
#                 cursor.execute("SELECT target FROM users WHERE id = %s", (user_id,))
#                 target = cursor.fetchone()[0]
#
#                 # Reja bajarilish foizi
#                 percent = (total_sales / target) * 100
#
#                 # Har bir kiritilgan savdo haqida hisobot yuborish
#                 await message.reply(
#                     f"Bugungi savdo qo'shildi: {sales_value}$.\n"
#                     f"Jami savdo: {total_sales}$.\n"
#                     f"Reja: {percent:.2f}% bajarildi."
#                 )
#
#                 # Agar 100% bajarilsa, ma'lumotlarni `monthly_reports` ga qo'shish
#                 if percent >= 100:
#                     # Ma'lumotlarni `monthly_reports` jadvaliga qo'shish
#                     cursor.execute(
#                         "INSERT INTO monthly_reports (user_id, month, year, total_sales, percent, day) VALUES (%s, %s, %s, %s, %s, %s)",
#                         (user_id, today.month, today.year, total_sales, percent, today.day))
#                     connection.commit()
#
#                     # Darajani aniqlash
#                     if total_sales < 26000:
#                         degree = "✔️"
#                     elif 26000 <= total_sales < 52000:
#                         degree = "☑️"
#                     else:
#                         degree = "✅"
#
#                     # Joriy sana va vaqtni olish
#                     datetimes = datetime.datetime.now()
#                     date = datetimes.strftime("%Y-%m-%d")
#                     time = datetimes.strftime("%H:%M:%S")
#
#                     cursor.execute("SELECT name FROM users WHERE telegram_id = %s", (user_id,))
#                     name = cursor.fetchone()[0]
#
#                     # Hisobot yuborish
#                     await message.reply(
#                         f"{date} | {time}\n\n"
#                         f"👤: {name}\n🆔: {message.from_user.id}\n\n"
#                         f"Savdo qo'shildi 💰: {sales_value}$.\n"
#                         f"Jami savdo 💹: {total_sales}$.\nReja: {percent:.2f}% bajarildi {degree}"
#                     )
#
#                     # `daily_sales` jadvalidan tozalash
#                     cursor.execute("DELETE FROM daily_sales WHERE user_id = %s AND date = %s", (user_id, today))
#                     connection.commit()
#
#                     # Yangi oyga o'tish uchun maqsadni yangilash (masalan, maqsadni yangilash)
#                     cursor.execute("UPDATE users SET target = target + 10000 WHERE id = %s", (user_id,))
#                     connection.commit()
#
#                     # Yangi savdo kiritish boshlanishi haqida xabar yuborish
#                     await message.reply(
#                         "Reja 100% bajarildi! Yangi oy uchun savdo boshlanadi. Yangi savdolarni kiritish mumkin.")
#
#                 cursor.close()
#                 connection.close()
#
#         else:
#             await message.reply("Savdoni faqat butun va haqiqiy sonlarda kiriting!")
#     else:
#         await message.answer("Siz shartnomachi emassiz!")
