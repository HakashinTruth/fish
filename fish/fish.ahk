SetBatchLines, -1
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

; variables
toggle := false
centerX := 960
centerY := 530
radius := 100   
speed := 0.05   
angle := 0

[:: 
toggle := !toggle
if (toggle) {
    ToolTip, BOT: SEARCHING (SMOOTH), 10, 10
    angle := 0
} else {
    ToolTip, BOT: STOPPED, 10, 10
    Sleep, 1000
    ToolTip
}

while (toggle)
{
    ; circular search
    foundBobber := false
    Loop, 20 
    {
        if (!toggle) 
            break

        angle += speed
        moveX := centerX + (Cos(angle) * radius)
        moveY := centerY + (Sin(angle) * radius)

        DllCall("SetCursorPos", "int", moveX, "int", moveY)

        ; Scan for bobber in ocean
        PixelSearch, bx, by, 200, 125, 1820, 1000, 0xCD3124, 60, Fast RGB
        if (!ErrorLevel) 
        {
            last_bx := bx
            last_by := by
            foundBobber := true
            break 
        }
        Sleep, 5 
    }

    if (!foundBobber)
        continue

    ; spam click until brown pixel apears at the cords
    ToolTip, BOBBER SPOTTED, 10, 10
    minigameDetected := false
    startClickTime := A_TickCount

    Loop
    {
        if (!toggle)
            break
            
        Click, %last_bx%, %last_by%
        
        ; Check 1453, 800 for Brown pixel
        PixelSearch, fx, fy, 1453, 800, 1453, 800, 0x5D4037, 60, Fast RGB
        if (!ErrorLevel) 
        {
            minigameDetected := true
            break 
        }

        if (A_TickCount - startClickTime > 4000)
        {
            ToolTip, BOT: TIMEOUT - NO MINIGAME - RESETTING, 10, 10
            Sleep, 500
            break 
        }

        Sleep, 100 
    }

    if (!minigameDetected)
        continue

    ; program stay idle during minigame
    ToolTip, BOT: MINIGAME ACTIVE, 10, 10
    Loop
    {
        if (!toggle)
            break

        ; Stay until brown pixel at 1453, 800 is gone
        PixelSearch, fx, fy, 1453, 800, 1453, 800, 0x5D4037, 60, Fast RGB
        if (ErrorLevel) 
            break 
            
        Sleep, 400 
    }

    ; loop sequence
    if (toggle)
    {
        ToolTip, BOT: WAITING , 10, 10
        Sleep, 2000 
        
        ; First Position: 1040, 620 , for any errors during after minigame, if fish fails it wil close the popup
        Click, 1040, 620
        Sleep, 1000 
        Click, 1040, 620
        Sleep, 1000 
        Click, 1040, 620
        Sleep, 1000 ; Gap before next position
        
        ; Second Position: 1400, 620 (2 times)
        Click, 1400, 620
        Sleep, 1000 
        Click, 1400, 620
        
        ToolTip, BOT: COOLDOWN 5s..., 10, 10
        Sleep, 5000 
        angle := 0 
    }
}
return