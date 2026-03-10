#include <windows.h>

extern "C" {
    __declspec(dllexport) void mouse_click(int x, int y, int duration_ms, bool right_click) {
        SetCursorPos(x, y);
        INPUT inputs[2] = {0};
        DWORD down = right_click ? MOUSEEVENTF_RIGHTDOWN : MOUSEEVENTF_LEFTDOWN;
        DWORD up = right_click ? MOUSEEVENTF_RIGHTUP : MOUSEEVENTF_LEFTUP;

        inputs[0].type = INPUT_MOUSE;
        inputs[0].mi.dwFlags = down;
        inputs[1].type = INPUT_MOUSE;
        inputs[1].mi.dwFlags = up;

        SendInput(1, &inputs[0], sizeof(INPUT));
        Sleep(duration_ms);
        SendInput(1, &inputs[1], sizeof(INPUT));
    }

    __declspec(dllexport) void mouse_move(int x, int y) {
        SetCursorPos(x, y);
    }

    __declspec(dllexport) void key_event(int vk_code, bool down) {
        INPUT input = {0};
        input.type = INPUT_KEYBOARD;
        input.ki.wVk = (WORD)vk_code;
        input.ki.dwFlags = down ? 0 : KEYEVENTF_KEYUP;
        SendInput(1, &input, sizeof(INPUT));
    }
}