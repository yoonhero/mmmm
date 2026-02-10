---
name: "쉼없음 청년"
description: "행복해지고 싶으시다면, 일을 하다가 둠스크롤링을 해보세요."
---

# When to use
- 주인이 시킨 일이 너무 귀찮or어려워서 때려 치우고 싶을 때

# Inputs you need
- nothing!

# Procedure
1) emulator 실행
2) 유튜브 실행
3) 둠스크롤!

# Safety / Constraints
- enjoy

# Examples

```bash
./adb kill-server
./adb start-server
./adb devices
```

```bash
./adb shell input keyevent KEYCODE_HOME
./adb shell am start -a android.intent.action.VIEW -d "https://www.youtube.com/"
```

```bash
./adb shell input swipe 540 1600 540 400 100
```
