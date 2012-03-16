--[[
Copyright (c) 2012, JDFight
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS 
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
OF SUCH DAMAGE.

--]]

--Menu Resources and Screens for BoxBreaker

local imagePath = "res/pixmaps/"

gameMode = "MENU_START" --"GAME_PLAY"  --"MENU_START"  "MENU_RESTART"  "MENU_END"

bgStart = love.graphics.newImage(imagePath.."bgTitle.png")
bgLevelClear = love.graphics.newImage(imagePath.."bgLevelClear.png")
btnPlay = love.graphics.newImage(imagePath.."btn_play.png")
btnNewGame = love.graphics.newImage(imagePath.."btn_newGame.png")
btnContinue = love.graphics.newImage(imagePath.."btn_continue.png")
bgGameOver = love.graphics.newImage(imagePath.."bgGameOver.png")
bgGameWon = love.graphics.newImage(imagePath.."bgGameWon.png")

gameContinue = false
gameReset = false
initGame = true

--PlayButton - clickzone bounds:
bxMin = 268
byMin = 304
bxMax = bxMin + 128
byMax = byMin + 37

bitPressed = false;
btnW = 128
btnH = 37
--bounds of buttons 0, 46, 128, 83

function drawMenu(strMenu)
   if strMenu == "MENU_START" then
     --draw start Menu
       love.graphics.draw(bgStart, 0, 0)
       love.graphics.draw(btnNewGame, 256, 270)
       love.graphics.draw(btnContinue, 256, 320)
       love.graphics.print("powered by ", 470, 453)
    elseif strMenu == "GAME_OVER" then
        love.graphics.draw(bgGameOver, 0, 0)
	love.graphics.print("Press Left Mouse button to Continue", 200, 280)
    end
end

function playPressed()
   love.mouse.setGrab(true)
   love.mouse.setVisible(false)
    gameReset = true
    gameMode = "GAME_RESET"
    bitPressed = true
end

function menuUpdate(strMenu)
   local mx, my = love.mouse.getPosition()
   if strMenu == "MENU_START" then
      love.mouse.setGrab(false)
      love.mouse.setVisible(true)
      if love.mouse.isDown("l") and bitPressed == false then
	 if (mx >= 256 and mx <= 256 + btnW and my >= 313 and my<=313 + btnH) then
	   -- print("Play Pressed!")
	    playPressed()
	    bitPressed = true
	 elseif (mx >= 256 and mx <= 256 + btnW  and my >= 363 and my <= 363 + btnH) then
	    print("CONTINUE")
	    gameContinue = true
	    playPressed()
	    bitPressed = true
         end
      elseif not love.mouse.isDown("l") and bitPressed then
	 bitPressed = false
      elseif love.joystick.isDown(0, 1) then
	 playPressed()
      end
   elseif strMenu == "GAME_OVER" then
     --if love.mouse.isDown("l") and bitPressed == false then
     if love.keyboard.isDown(" ") or love.joystick.isDown(0, 0) or love.mouse.isDown('l') then
	 gameMode = "MENU_START"
      end

   end
end