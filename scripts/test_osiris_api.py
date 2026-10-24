import asyncio
import json
import nodriver as uc

async def main():
    # Запускаем браузер с видимым окном (headless=False).
    # Cloudflare гораздо лояльнее к видимым браузерам[reference:1].
    browser = await uc.start(
    headless=False,
    browser_executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    )
    
    url = "https://osirisai.live/api/cctv?region=texas"
    print(f"Открываю {url} в реальном браузере...")
    
    page = await browser.get(url)
    
    print("Ожидание прохождения проверки Cloudflare (до 30 секунд)...")
    # Ждём, пока в теле страницы не появится JSON (символ '{').
    # Если Cloudflare пропустит, это произойдёт автоматически[reference:2].
    try:
        await page.wait_for(lambda: page.evaluate('document.body.innerText.trim().startsWith("{")'), timeout=30)
        print("✅ Проверка Cloudflare пройдена!")
    except Exception:
        print("⚠️ Не удалось дождаться прохождения проверки за 30 секунд.")
        print("Возможно, Cloudflare требует ручного вмешательства (например, клика по чекбоксу).")
        # Всё равно попробуем прочитать содержимое
        pass
    
    # Получаем текст страницы
    content = await page.evaluate('document.body.innerText')
    
    print(f"Длина ответа: {len(content)} символов")
    print("Первые 1000 символов:")
    print(content[:1000])
    
    # Пытаемся распарсить JSON
    try:
        data = json.loads(content)
        print("\n✅ Успех! Ответ является валидным JSON.")
        if isinstance(data, dict):
            print("Ключи в ответе:", list(data.keys())[:10])
        elif isinstance(data, list):
            print(f"Получен список из {len(data)} элементов. Первый элемент:")
            print(json.dumps(data[0], indent=2)[:500])
    except json.JSONDecodeError:
        print("\n⚠️ Ответ не является JSON. Возможно, Cloudflare всё ещё блокирует.")
    
    # Даём время посмотреть результат
    input("Нажмите Enter, чтобы закрыть браузер...")
    browser.stop()

if __name__ == "__main__":
    uc.loop().run_until_complete(main())