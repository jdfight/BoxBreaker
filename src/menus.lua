--Menu Screens for Breakout

local imagePath = "res/pixmaps/"

gameMode = "MENU_START" --"GAME_PLAY"  --"MENU_START"  "MENU_RESTART"  "MENU_END"

bgStart = love.graphics.newImage(imagePath.."bgTitle.png")
bgLevelClear = love.graphics.newImage(imagePath.."bgLevelClear.png")
btnPlay = love.graphics.newImage(imagePath.."btn_play.png")
bgGameOver = love.graphics.newImage(imagePath.."bgGameOver.png")
bgGameWon = love.graphics.newImage(imagePath.."bgGameWon.png")
gameReset = false
initGame = true

--PlayButton - clickzone bounds:
bxMin = 268
byMin = 304
bxMax = bxMin + 100
byMax = byMin + 48

bitPressed = false;

function drawMenu(strMenu)
   if strMenu == "MENU_START" then
     --draw start Menu
       love.graphics.draw(bgStart, 0, 0)
       love.graphics.draw(btnPlay, 256, 300)
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
	 if (mx >= bxMin and mx <= bxMax and my >= byMin and my<=byMax) then
	   -- print("Play Pressed!")
	    playPressed()
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