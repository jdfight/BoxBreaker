require "maps"
require "BObjects"
require "menus"

screenWidth = 640
screenHeight = 480

saveData = "1"
text = "<ESC> Quit,  <Q> Release Mouse, <Space> Launch Ball <S> Toggle Sound"

ballHit = false
wallHit = false
brickHit = false
ceilingHit = false
ballAlive = false
ballReset = false
gameStarted = false
initGame = true

bitMouseDown = false
bonusDropping = false

currentLevel = 1
savedLevel = 1
maxLevel = 15
paused = false

ammo = 0
intLives = 5

impactX = 0
impactY = 0
--rot = 0;
world = nil

fireworksCounter = 0
fireworksTime = 10

fileSave = nil

function resetStats()
   text = "<ESC> Quit,  <Q> Release Mouse, <Space> Launch Ball <S> Toggle Sound"

   ballHit = false
   wallHit = false
   brickHit = false
   ceilingHit = false
   ballAlive = false
   ballReset = false

   bitMouseDown = false
   bonusDropping = false
   if gameContinue == true then
     currentLevel = savedLevel
   else 
      currentLevel = 1 
      --local success = love.filesystem.write("boxSave", tostring(currentLevel))
	-- if success then
	  --  print("Game Saved")
	 -- end
    end
   gameContinue = false

   print("CURRENT LEVEL = "..currentLevel)
   ammo = 0
   intLives = 5

   impactX = 0
   impactY = 0
   score = 0;
  
   intBalls = 0
   score = 0;
   gameReset = false
   drawMap()
  end

function setupWorld()
   world = love.physics.newWorld(-640, -480, 640, 480)
   world:setAllowSleep(true)
   world:setGravity(0,100)
   world:setMeter(72)
   world:setCallbacks(add, persist, rem, result)
  end

function love.load()
    
   if love.filesystem.exists("boxSave") == false then
      love.filesystem.newFile("boxSave")
      love.filesystem.write("boxSave", tostring(currentLevel))
   else
      for data in love.filesystem.lines("boxSave") do
	 saveData = data
      end
      savedLevel = tonumber(saveData)
      print("SaveData Found "..saveData.."-- "..currentLevel)
   end

   setupWorld();
  -- love.graphics.setMode(screenWidth,screenHeight, false, true, 0)
   love.graphics.setCaption("Box Breaker")
   setupObjects()
  -- drawMap()   
end

function checkKeys()
     if love.keyboard.isDown("q") then
        love.mouse.setGrab(false)
	love.mouse.setVisible(true)
     end
     if love.keyboard.isDown("escape") then
         love.event.push('q')
      end
     if love.keyboard.isDown("s") then
        if soundEnabled == true then
	    soundEnabled = false
	else soundEnabled = true
	end
     end
end

function love.update(dt)
   --print(love.joystick.getAxis(0,0))
   
   if paused then return end
   if gameMode == "GAME_PLAY" or gameMode == "LEVEL_CLEAR" or gameMode == "GAME_WON" then
      checkKeys()
      gameUpdate(dt)
   elseif gameMode == "GAME_OVER" then
      menuUpdate(gameMode)
   elseif gameMode=="MENU_START" then
      menuUpdate(gameMode)
      paddleX = love.mouse.getX() - paddle:getWidth()/2
       if love.keyboard.isDown("escape") then
	  love.event.push('q')
       end
   elseif gameMode == "GAME_RESET" then
      if not initGame then
        killWorldObjects()
     elseif initGame then
	initGame = false
     end
      resetStats()
  --    createBall("Ball"..ballNum, 100, 100, false)
       for i in pairs(objects.balls) do
       	  objects.balls[i].body:setX(paddleX + 32) 
	  objects.balls[i].body:setY(paddleY - 10)
      end
      gameMode = "GAME_PLAY"
   end
   
end

function checkGameplayKeys()

     if love.mouse.isDown("l") or love.joystick.isDown(0, 1) then 
        if  ammo > 0 and ballAlive == true and bitMouseDown == false then
	   createBullet("Bullet"..bulletNum,paddleX+32, paddleY )
	   bitMouseDown = true
	   ammo = ammo - 1
	end
	if gameMode == "LEVEL_CLEAR" then
	   drawMap()
	   bitMouseDown = true
	   gameMode = "GAME_PLAY"
	end
	if gameMode == "GAME_WON" then
	   gameMode = "MENU_START"
	end
     elseif love.mouse.isDown("l") == false then
	bitMouseDown = false
     end
     if (love.mouse.isDown("r")or love.joystick.isDown(0, 0)) and gameMode == "GAME_PLAY" then
	if ballAlive == false then 
	   ballReset = false
	   ballAlive = true;
	   playSound(sfx_serve)
	   if gameStarted == false then
	      gameStarted = true
	   end
	end
     end 
  end

function gameUpdate(dt)
    
   world:update(dt)
   checkGameplayKeys()
   
     local intBalls = 0
     for i in pairs(objects.balls) do
	 bx, by = objects.balls[i].body:getPosition()
         if(objects.balls[i].markedForDeath == true) then
	
	  objects.balls[i].shape:destroy()
	  objects.balls[i].body:destroy()
	  objects.balls[i] = nil
        
	 elseif(objects.balls[i].markedForDeath == false) then
	    intBalls = intBalls+1
	    if objects.balls[i].ballHit==true then	    
	       impactX = bx - objects.paddle.body:getX();
    	       objects.balls[i].body:applyImpulse(impactX * 10, -640, 0, 0) 
               objects.balls[i].ballHit = false;
	       playSound(sfx_reflect)
	    elseif  objects.balls[i].wallHit == true then

	       objects.balls[i].body:applyImpulse(-objects.balls[i].impactX, 0, 0, 0) 
	       objects.balls[i].wallHit = false;
	   
	    elseif  objects.balls[i].ceilingHit == true then

	       objects.balls[i].body:applyImpulse(0 ,-objects.balls[i].impactY, 0, 0) 
	       objects.balls[i].ceilingHit = false;

	    elseif objects.balls[i].brickHit == true then
	       objects.balls[i].body:applyImpulse(objects.balls[i].impactX * 10 ,-objects.balls[i].impactY, 0, 0) 
	       objects.balls[i].brickHit = false;
	       playSound(arrSoundBooms[intBoomIdx])
	       intBoomIdx = intBoomIdx+1
	       if intBoomIdx > 2 then
	          intBoomIdx = 0
	       end
	    
	   end
      	  
           ax, ay = objects.balls[i].body:getLinearVelocity() 
           if(ay == 0 and ballAlive == true) then
	      objects.balls[i].intIdleFrames = objects.balls[i].intIdleFrames + 1
	      if(objects.balls[i].intIdleFrames >= 1) then
	         --print("Pop UP!")
		 objects.balls[i].body:applyImpulse(0, -100, 0, 0)
	      end
	   elseif (ay ~= 0) then objects.balls[i].intIdleFrames = 0 end
	   
           local setSpeed = false
	   if(ay > 640) then
	     ay = 640
	      setSpeed = true
	   elseif (ay < -640) then
	     ay = -640
	      setSpeed = true
	   end
	   if(ax > 480) then
	     ax = 480
	      setSpeed = true
	   elseif (ax < -480) then
	     ax = -480
	      setSpeed = true
	   end
	   if setSpeed == true then
	      objects.balls[i].body:setLinearVelocity(ax, ay)
	   end
	   
	  
	end
 
     end
     if ballReset == true then
	ballReset = false
     end
     if ballAlive == false then
	for i in pairs(objects.balls) do
       	    objects.balls[i].body:setX(paddleX + 32) 
	    objects.balls[i].body:setY(paddleY - 10)
	end
     end
     --dt mod
     local dtMod = (dt * 1000)
     if love.joystick.getAxis (0, 0) < -0.15 then
        paddleX = paddleX + (love.joystick.getAxis(0, 0) * dtMod)
	love.mouse.setPosition(paddleX +32, paddleY + 8)
     elseif love.joystick.getAxis (0, 0) > 0.15  then
        paddleX = paddleX + (love.joystick.getAxis(0, 0) * dtMod)
	 love.mouse.setPosition(paddleX +32, paddleY + 8)
     else 
	paddleX = love.mouse.getX() - paddle:getWidth()/2
     end
     if paddleX < 0 then 
	paddleX = 0
     elseif paddleX > screenWidth - paddle:getWidth() then 
  	paddleX = screenWidth - paddle:getWidth()
     end

     objects.paddle.body:setX(paddleX + paddle:getWidth()/2)
     objects.paddle.body:setY(paddleY + paddle:getHeight()/2)
     -- objects.ball.body:applyTorque(rot)
     -- rot = rot + 1;
     -- if rot > 360 then
     --    rot = 0
  --end 
      
 --
   -- for i in pairs(objects.balls) do
  --  end
 -- print(intBalls)
  if(intBalls == 0 and ballAlive == true) then
      ballReset = true;
      ballAlive = false;
      intLives = intLives - 1;
      -- print(intLives)
      if intLives <= 0 then
	 intLives = 0
	 --print("GAME OVER")
        -- strMessage = "GAME OVER";
	 return
      elseif intLives > 0 then
	 ammo = 0
	 createBall("Ball"..ballNum, 320, 465, false)
	 for i in pairs(objects.bonuses) do
	    if objects.bonuses[i].markedForDeath ~= true then
	       objects.bonuses[i].body:setY(600)
	    end 
	 end
	 for i in pairs(objects.bullets) do
	    if objects.bullets[i].markedForDeath ~= true then
	       objects.bullets[i].body:setY(-100)
	    end
	 end
      end
   end

   for i in pairs(objects.explosions) do
     --if i > 0 then
    -- print(i)
    -- if(objects.explosions[i].markedForDeath == true) then
     if(objects.explosions[i].body:getY() > 525) then
	objects.explosions[i].shape:destroy()
	objects.explosions[i].body:destroy()
	objects.explosions[i].image = nil
	objects.explosions[i] = nil	
     end
  end
   for i in pairs(objects.bricks) do
       if(objects.bricks[i].markedForDeath == true) then
	
	  objects.bricks[i].shape:destroy()
	  objects.bricks[i].body:destroy()
	  objects.bricks[i].image = nil
	  objects.bricks[i] = nil
	--table.remove(objects.explosions[i])
      end
   end
 
   for i in pairs(objects.bonuses) do

      -- if(objects.bonuses[i].markedForDeath == true) then
      if(objects.bonuses[i].body:getY() > 525) then
	  objects.bonuses[i].shape:destroy()
	  objects.bonuses[i].body:destroy()
	 -- objects.bonuses[i].image = nil
	  objects.bonuses[i] = nil
	--table.remove(objects.explosions[i])
      end
   end
    for i in pairs(objects.bullets) do

      if(objects.bullets[i].markedForDeath == true and objects.bullets[i].body:getX() < 0) then
	  objects.bullets[i].shape:destroy()
	  objects.bullets[i].body:destroy()
	 -- objects.bonuses[i].image = nil
	  objects.bullets[i] = nil
	--table.remove(objects.explosions[i])
       elseif (objects.bullets[i].body:getY() < 0) then
	 -- killBullet(i);
	  killObject(objects.bullets[i])
       end
   end
   
   for i in pairs(objects.bombs) do

      if(objects.bombs[i].markedForDeath == true and objects.bombs[i].body:getX() < 0) then
	  objects.bombs[i].shape:destroy()
	  objects.bombs[i].body:destroy()
	 -- objects.bonuses[i].image = nil
	  objects.bombs[i] = nil
	--table.remove(objects.explosions[i])
      end
   end 
end

function drawMap()
   arrMap = getMap(currentLevel)
   tx = 0 
   ty = 10
   brickNum = 0
   for y=1, 16 do
      for x=1, 20 do                                     
	 if arrMap[y][x] ~= 0 then                   
	    createBrick("Brick"..brickNum, tx, ty, arrMap[y][x]);
	    brickNum = brickNum+1;   
         end
	  tx = tx+34
      end
      tx = 0
      ty = ty+18
     
   end
   createBall("Ball"..ballNum, 100, 100, false)
  
end

	 
function love.draw()
   if gameMode=="GAME_PLAY" or gameMode == "LEVEL_CLEAR" or gameMode == "GAME_WON" then
         drawGame()
	 if gameMode == "GAME_WON" then
	    fireworksCounter = fireworksCounter + 1
	    if fireworksCounter > fireworksTime then
	       createExplosion("Explosion", math.ceil(math.random(640)),  math.ceil(math.random(240)), 100, 100, explosionColors[math.ceil(math.random(# explosionColors))])
	       fireworksCounter = 0
	       fireworksTime = math.ceil(math.random(30, 60))
            end
	 end
   elseif gameMode == "MENU_START" then
	 drawMenu(gameMode)
   elseif gameMode == "GAME_OVER" then
	 drawMenu(gameMode)
   end
end

function drawGame()
  love.graphics.setColor(255, 255, 255) 
  if gameMode == "GAME_PLAY" then
     love.graphics.draw(bg, 0, 0)
     if ballAlive == false then
        love.graphics.print("Right Click to Launch Ball ", 240,400)
     end
  elseif gameMode == "LEVEL_CLEAR" then
     love.graphics.draw(bgLevelClear, 0, 0)
     love.graphics.print("Click Left Mouse Button to Continue", 200, 280)
   elseif gameMode == "GAME_WON" then
     love.graphics.draw(bgGameWon, 0, 0)
     love.graphics.print("Click Left Mouse Button to Continue", 212, 310)
  end
  love.graphics.draw(paddle, paddleX, paddleY)
  love.graphics.setColor(193, 47, 14)  
 
  love.graphics.setColor(255, 255, 255) 
--  love.graphics.draw(ball, objects.ball.body:getX() - ball:getWidth()/2, objects.ball.body:getY() - ball:getHeight()/2)
  if intLives > 0 then
     local count = 0
     for i in pairs(objects.balls) do 
	local by = objects.balls[i].body:getY()
	if (by < 500) then
	   if(objects.balls[i].isBomb == true) then
	      love.graphics.draw(ballBomb, objects.balls[i].body:getX() - ballBomb:getWidth()/2, by - ballBomb:getHeight()/2)	
	      elseif(objects.balls[i].isBomb == false) then
	      love.graphics.draw(ball, objects.balls[i].body:getX() - ball:getWidth()/2, by - ball:getHeight()/2)
	   end
	elseif (by > 500) then
	--killBall(i)
	   killObject(objects.balls[i])
	end
     end
     for i in pairs(objects.bricks) do
	local brY = objects.bricks[i].body:getY()
	if(brY > 0) then
	   love.graphics.draw(objects.bricks[i].avatar, objects.bricks[i].body:getX() - brick:getWidth()/2 , brY - brick:getHeight()/2)
	   count = count + 1
	end
     end
     for i in pairs(objects.explosions) do
	love.graphics.draw(objects.explosions[i].avatar, objects.explosions[i].body:getX() - objects.explosions[i].avatar:getWidth()/2 , objects.explosions[i].body:getY() - objects.explosions[i].avatar:getHeight()/2)
     end
 
     for i in pairs(objects.bonuses) do
	bnY =  objects.bonuses[i].body:getY()
	if string.find(i, "BonusB")~= nil and bnY < 465 then
	   love.graphics.draw(bonusBall, objects.bonuses[i].body:getX() - bonusBall:getWidth()/2 , bnY - bonusBall:getHeight()/2)
	elseif string.find(i, "BonusP") ~= nil and bnY < 465 then
	     love.graphics.draw(bonusImage, objects.bonuses[i].body:getX() - bonusImage:getWidth()/2 , bnY - bonusImage:getHeight()/2)
	elseif string.find(i, "BonusS") ~= nil and bnY < 465 then
	     love.graphics.draw(bonusShot, objects.bonuses[i].body:getX() - bonusShot:getWidth()/2 , bnY - bonusShot:getHeight()/2)
	elseif string.find(i, "BonusM") ~= nil and bnY < 465 then
	     love.graphics.draw(bonusMultiBall, objects.bonuses[i].body:getX() - bonusMultiBall:getWidth()/2 , bnY - bonusMultiBall:getHeight()/2)
      
	elseif string.find(i, "BonusC") ~= nil and bnY < 465 then
	     love.graphics.draw(bonusBomb, objects.bonuses[i].body:getX() - bonusBomb:getWidth()/2 , bnY - bonusBomb:getHeight()/2) 
       
	  elseif string.find(i, "BonusL") ~= nil and bnY < 465 then
	     love.graphics.draw(bonusPaddle, objects.bonuses[i].body:getX() - bonusPaddle:getWidth()/2 , bnY - bonusPaddle:getHeight()/2) 
    
	  end
       end

       for i in pairs(objects.bullets) do
	  blY =  objects.bullets[i].body:getY()
	  love.graphics.draw(bullet, objects.bullets[i].body:getX() - bullet:getWidth()/2 , blY - bullet:getHeight()/2)
       end

       text = " "..count
       if gameMode == "GAME_PLAY" and count == 0 then
	  text = "You Won!"
	  currentLevel = currentLevel+1;
	  if currentLevel > maxLevel then
	     text = "Congratulations!"
            -- print(maxLevel)
	     --print ("END GAME?")
	     gameMode = "GAME_WON"
	  else
	 for i in pairs(objects.explosions) do
	    if objects.explosions[i].markedForDeath ~= true then
	      -- killExplosion(i)
	       killObject(objects.explosions[i])
	    end
	 end
	  for i in pairs(objects.bonuses) do
	    if objects.bonuses[i].markedForDeath ~= true then
	       --killBonus(i)
	       killObject(objects.bonuses[i])
	       objects.bonuses[i].body:setY(600)	
	    end
	 end
	 for i in pairs(objects.balls) do
	    if objects.balls[i].markedForDeath ~= true then
	      -- killBall(i)
	       objects.balls[i].ballReset = true;
	       objects.balls[i].ballAlive = false;
	       killObject(objects.balls[i])
	    end
	 end
         for i in pairs(objects.bullets) do
	    if objects.bullets[i].markedForDeath ~= true then
	       --killBullet(i)
	       killObject(objects.bullets[i])
	    end
	 end
	 killWorldObjects()
	 if gameMode ==  "GAME_PLAY" then
	    gameMode = "LEVEL_CLEAR"
	    if savedLevel < currentLevel then
	       local success = love.filesystem.write("boxSave", tostring(currentLevel))
	       if success then
		  print("Game Saved")
	       end
            end
	 end
	    --drawMap()
     end
        ballReset = true
        ballAlive = false
     end
 end
  if(ammo > 0) then
     love.graphics.print("Click M1 to Shoot: Ammo: "..ammo, 225,4)
  end
  if (intLives <= 0) then     
      gameMode = "GAME_OVER"
      return

  end
  if paused then
     love.graphics.print("Paused",300,200)
  end
  love.graphics.print("Score: "..score,8,4)
  love.graphics.print("Lives: "..intLives, 580,4)
end

function add(a, b, coll)
   if ballAlive == true then
    if (a == "Paddle" and string.find(b, "Ball")) then --or (string.find(a, "Ball") and b == "Paddle") then
       if(objects.balls[b].ballHit ~= true) then
	   objects.balls[b].impactX, objects.balls[b].impactY = coll:getVelocity()
	   objects.balls[b].ballHit = true;
	end
    elseif (a == "Wall" and string.find(b, "Ball")) then 
        objects.balls[b].impactX, objects.balls[b].impactY = coll:getVelocity();
        objects.balls[b].wallHit = true;
    elseif (a == "Ceiling" and string.find(b, "Ball") ~= nil) then 
       objects.balls[b].impactX, objects.balls[b].impactY = coll:getVelocity();
       objects.balls[b].ceilingHit = true;
    elseif ballAlive == true and string.find(a, "Brick") ~= nil and string.find(b, "Ball") ~= nil then
       if not objects.balls[b].isBomb == true then
          healBrickHP(a, -1)
       end
       objects.balls[b].impactX, objects.balls[b].impactY = coll:getVelocity();
       objects.balls[b].impactX = objects.balls[b].body:getX() - objects.bricks[a].body:getX();
       local brickX, brickY = objects.bricks[a].body:getPosition()
       if (objects.bricks[a].intHP <= 0) then	
	  createExplosion("Explosion", objects.bricks[a].body:getX(), objects.bricks[a].body:getY(), impactX, impactY)
	  if (objects.bricks[a].body:getX() > 0) then
	     if(math.random(100) > 75 and bonusDropping == false) then
		bonusDropping = true
		createBonus(objects.bricks[a].body:getX(), objects.bricks[a].body:getY())
	     end 
	     objects.bricks[a].body:setX(objects.bricks[a].body:getX() * -1)
	     objects.bricks[a].body:setY(objects.bricks[a].body:getY() * -1)
	  end
	 if(objects.bricks[a].markedForDeath == false) then
	    objects.bricks[a].markedForDeath = true;
	 end
         
      end
      
       score = score + 100
       objects.balls[b].brickHit = true;
       if(objects.balls[b].isBomb == true) then
	  objects.balls[b].isBomb = false;
          createBomb("Bomb"..bombNum, brickX, brickY)
	  
       end
     elseif (string.find(b,"Bonus") ~= nil and a == "Paddle")  then
       if(objects.bonuses[b].markedForDeath == false) then
          activateBonus(b)
       end
    elseif (string.find(a,"Brick") and string.find(b, "Bullet") ~= nil) then 
       --printme(explosionColors[objects.bricks[a].intHP - 1]) 
       if objects.bricks[a].intHP - 1 > 0 then
	  createExplosion("Explosion", objects.bricks[a].body:getX(), objects.bricks[a].body:getY(), impactX, impactY, explosionColors[objects.bricks[a].intHP])
       elseif  objects.bricks[a].intHP - 1 < 1 then
          createExplosion("Explosion", objects.bricks[a].body:getX(), objects.bricks[a].body:getY(), impactX, impactY, "red")
       end
       if objects.bullets[b].markedForDeath == false then
	     --killBullet(b)
	     killObject(objects.bullets[b])
	     score = score + 100 
       end
        if (objects.bricks[a].body:getX() > 0) then
	     objects.bricks[a].body:setX(objects.bricks[a].body:getX() * -1)
	     objects.bricks[a].body:setY(objects.bricks[a].body:getY() * -1)
	  end
	 if(objects.bricks[a].markedForDeath == false) then
	    objects.bricks[a].markedForDeath = true;
	    
	 end 
      --end

    elseif (string.find(a,"Brick") and string.find(b, "Bomb") ~= nil) then 
       createExplosion("Explosion", objects.bricks[a].body:getX(), objects.bricks[a].body:getY(), impactX, impactY, explosionColors[objects.bricks[a].intHP])
       if objects.bombs[b].markedForDeath == false then
	    -- killBomb(b)
	     killObject(objects.bombs[b])
	     score = score + 100 
       end
        if (objects.bricks[a].body:getX() > 0) then
	     objects.bricks[a].body:setX(objects.bricks[a].body:getX() * -1)
	     objects.bricks[a].body:setY(objects.bricks[a].body:getY() * -1)
	  end
	 if(objects.bricks[a].markedForDeath == false) then
	    objects.bricks[a].markedForDeath = true;
	    
	 end 
       end
  end
end


function killObject(obj)
    obj.isDead = true
    obj.body:setMass(0,0,0,0)
    if obj.body:getX() > 0 then
	  obj.body:setX(obj.body:getX() * -1) 
    end
    obj.markedForDeath = true;
    

 end

function love.keypressed(k)
   if gameMode=="GAME_PLAY" and k == 'p' then
	love.mouse.setGrab(paused)
	paused = not paused
	love.mouse.setVisible(paused)
	if not paused == true then
	   love.mouse.setPosition(paddleX +32, paddleY + 8)
	end
   end
end

