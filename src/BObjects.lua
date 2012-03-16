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

--Objects Resources and Methods for BoxBreaker
 imagePath = "res/pixmaps/"
 audioPath = "res/audio/"

soundEnabled = true
maxAudioTracks = 5

score = 0;
paddleY = 0
paddleX = 0

intBalls = 0
bonusNum = 0
ballNum = 0
bulletNum = 0
bombNum = 0

explosions = {}
explosionCount = 0;
explosionColors = {"red", "blue", "yellow", "green", "orange", "purple", "black", "silver"} 

 -- brick = love.graphics.newImage("brick.png")
  -- brick2 = love.graphics.newImage("brick_blue.png")
  -- brick3 = love.graphics.newImage("brick_gold.png")
  -- brick4 = love.graphics.newImage("brick_green.png")
  -- brick5 = love.graphics.newImage("brick_orange.png")
  -- brick6 = love.graphics.newImage("brick_purple.png")
  -- brick7 = love.graphics.newImage("brick_black.png")


sfx_boom = love.audio.newSource(audioPath.."sfx-01b.mp3", "static")
sfx_boom2 = love.audio.newSource(audioPath.."sfx-01b.mp3", "static")
sfx_boom3 = love.audio.newSource(audioPath.."sfx-01b.mp3", "static")
sfx_serve = love.audio.newSource(audioPath.."sfx-02.mp3", "static")
sfx_reflect = love.audio.newSource(audioPath.."sfx-05.mp3", "static")
sfx_death = love.audio.newSource(audioPath.."sfx-01.mp3", "static")
sfx_bonus = love.audio.newSource(audioPath.."sfx-06.mp3", "static")
sfx_shot = love.audio.newSource(audioPath.."sfx-09.mp3", "static")

arrSoundBooms = {} 
arrSoundBooms[0] = sfx_boom 
arrSoundBooms[1] = sfx_boom2 
arrSoundBooms[2] = sfx_boom3
intBoomIdx = 0


function setupObjects()
   bg  = love.graphics.newImage(imagePath.."bg1.png")
   paddle = love.graphics.newImage(imagePath.."paddle.png")
   brick = love.graphics.newImage(imagePath.."brick.png")
   brick2 = love.graphics.newImage(imagePath.."brick_blue.png")
   brick3 = love.graphics.newImage(imagePath.."brick_gold.png")
   brick4 = love.graphics.newImage(imagePath.."brick_green.png")
   brick5 = love.graphics.newImage(imagePath.."brick_orange.png")
   brick6 = love.graphics.newImage(imagePath.."brick_purple.png")
   brick7 = love.graphics.newImage(imagePath.."brick_black.png")
   brick8 = love.graphics.newImage(imagePath.."brick_silver.png")
   
   ball = love.graphics.newImage(imagePath.."ball.png")
   ballBomb = love.graphics.newImage(imagePath.."ball_bomb.png");
   bonusImage = love.graphics.newImage(imagePath.."bonus_gold.png")
   bonusBall = love.graphics.newImage(imagePath.."bonus_ball.png")
   bonusShot = love.graphics.newImage(imagePath.."bonus_shot.png")
   bonusBomb = love.graphics.newImage(imagePath.."bonus_bomb.png")
   bonusPaddle = love.graphics.newImage(imagePath.."bonus_paddle.png")
   bonusMultiBall = love.graphics.newImage(imagePath.."bonus_ballMulti.png")
   bullet = love.graphics.newImage(imagePath.."bullet.png");

   p1 = love.graphics.newImage(imagePath.."p1.png")
   p2 = love.graphics.newImage(imagePath.."p2.png")
   p3 = love.graphics.newImage(imagePath.."p3.png")
   p4 = love.graphics.newImage(imagePath.."p4.png")
   p5 = love.graphics.newImage(imagePath.."p5.png")
  
   p1_orange = love.graphics.newImage(imagePath.."p1_orange.png")
   p2_orange = love.graphics.newImage(imagePath.."p2_orange.png")
   p3_orange = love.graphics.newImage(imagePath.."p3_orange.png")
   p4_orange = love.graphics.newImage(imagePath.."p4_orange.png")
   p5_orange = love.graphics.newImage(imagePath.."p5_orange.png")
  
   p1_yellow = love.graphics.newImage(imagePath.."p1_yellow.png")
   p2_yellow = love.graphics.newImage(imagePath.."p2_yellow.png")
   p3_yellow = love.graphics.newImage(imagePath.."p3_yellow.png")
   p4_yellow = love.graphics.newImage(imagePath.."p4_yellow.png")
   p5_yellow = love.graphics.newImage(imagePath.."p5_yellow.png")

   p1_green = love.graphics.newImage(imagePath.."p1_green.png")
   p2_green = love.graphics.newImage(imagePath.."p2_green.png")
   p3_green = love.graphics.newImage(imagePath.."p3_green.png")
   p4_green = love.graphics.newImage(imagePath.."p4_green.png")
   p5_green = love.graphics.newImage(imagePath.."p5_green.png")

   p1_blue = love.graphics.newImage(imagePath.."p1_blue.png")
   p2_blue = love.graphics.newImage(imagePath.."p2_blue.png")
   p3_blue = love.graphics.newImage(imagePath.."p3_blue.png")
   p4_blue = love.graphics.newImage(imagePath.."p4_blue.png")
   p5_blue = love.graphics.newImage(imagePath.."p5_blue.png")

   p1_purple = love.graphics.newImage(imagePath.."p1_purple.png")
   p2_purple = love.graphics.newImage(imagePath.."p2_purple.png")
   p3_purple = love.graphics.newImage(imagePath.."p3_purple.png")
   p4_purple = love.graphics.newImage(imagePath.."p4_purple.png")
   p5_purple = love.graphics.newImage(imagePath.."p5_purple.png")
 
   p1_black = love.graphics.newImage(imagePath.."p1_black.png")
   p2_black = love.graphics.newImage(imagePath.."p2_black.png")
   p3_black = love.graphics.newImage(imagePath.."p3_black.png")
   p4_black = love.graphics.newImage(imagePath.."p4_black.png")
   p5_black = love.graphics.newImage(imagePath.."p5_black.png")
   
   p1_silver = love.graphics.newImage(imagePath.."p1_silver.png")
   p2_silver = love.graphics.newImage(imagePath.."p2_silver.png")
   p3_silver = love.graphics.newImage(imagePath.."p3_silver.png")
   p4_silver = love.graphics.newImage(imagePath.."p4_silver.png")
   p5_silver = love.graphics.newImage(imagePath.."p5_silver.png")
   
   pieces = { p1, p2, p3, p4, p5 }
   pieces_orange = { p1_orange, p2_orange, p3_orange, p4_orange, p5_orange }
   pieces_yellow = { p1_yellow, p2_yellow, p3_yellow, p4_yellow, p5_yellow }
   pieces_green = { p1_green, p2_green, p3_green, p4_green, p5_green }
   pieces_blue = { p1_blue, p2_blue, p3_blue, p4_blue, p5_blue }
   pieces_purple = { p1_purple, p2_purple, p3_purple, p4_purple, p5_purple }
   pieces_black = { p1_black, p2_black, p3_black, p4_black, p5_black }
   pieces_silver = { p1_silver, p2_silver, p3_silver, p4_silver, p5_silver }
  

   paddleY = screenHeight - paddle:getHeight();

   objects = {}
   explosions = {}

   objects.ground = {}
   objects.ground.body = love.physics.newBody(world, 320, 495, 0, 0)
   objects.ground.shape = love.physics.newRectangleShape(objects.ground.body, 0, 0, 640, 30, 0)
   objects.ground.shape:setData("Ground");
   objects.ground.shape:setCategory(6)

   objects.wall_L = {}
   objects.wall_L.body = love.physics.newBody(world, 0, 240, 0, 0)
   objects.wall_L.shape = love.physics.newRectangleShape(objects.wall_L.body, 0, 0, 10, 550, 0)
   objects.wall_L.shape:setData("Wall");
   
   objects.wall_R = {}
   objects.wall_R.body = love.physics.newBody(world, 640, 240, 0, 0)
   objects.wall_R.shape = love.physics.newRectangleShape(objects.wall_R.body, 0, 0, 10, 550, 0)
   objects.wall_R.shape:setData("Wall");

   objects.ceiling = {}
   objects.ceiling.body = love.physics.newBody(world, 320, 0, 0, 0)
   objects.ceiling.shape = love.physics.newRectangleShape(objects.ceiling.body, 0, 0, 640, 10, 0)
   objects.ceiling.shape:setData("Ceiling");
   objects.ceiling .shape:setCategory(9)

   objects.paddle = {}
   objects.paddle.body = love.physics.newBody(world, 0, 0, 0, 0)
   objects.paddle.shape = love.physics.newRectangleShape(objects.paddle.body, 0, 0, paddle:getWidth(), paddle:getHeight(), 0) 
   objects.paddle.body:setBullet(true)
   objects.paddle.shape:setData("Paddle")
   objects.paddle.shape:setCategory(2)
 
   objects.balls = {}

   objects.bricks = {}
   objects.explosions = {}
   objects.bonuses = {}
   objects.bullets = {}
   objects.bombs = {}
end

function killObject(obj)
    obj.isDead = true
    obj.body:setMass(0,0,0,0)
    if obj.body:getX() > 0 then
	  obj.body:setX(obj.body:getX() * -1) 
    end
    obj.markedForDeath = true;
 end

function createBrick(name, bx,by,hp)
   objects.bricks[name] = {}
   objects.bricks[name].body = love.physics.newBody(world, bx, by, 0, 0) 
   objects.bricks[name].shape = love.physics.newRectangleShape(objects.bricks[name].body, 0, 0, 32, 16, 0) 
   objects.bricks[name].body:putToSleep()
   objects.bricks[name].markedForDeath = false;
   objects.bricks[name].shape:setData(name)
   objects.bricks[name].shape:setCategory(3)
   objects.bricks[name].intHP = hp
   objects.bricks[name].intIdleFrames = 0;
   setBrickAvatar(name) 
end
  
function createBallSplosion()
      for i = 1, 10 do
	 createBall("Ball"..ballNum, 320, 4)
          objects.balls["Ball"..ballNum - 1].body:applyImpulse( math.random(-480,480), -math.random(-640, 640), 0, 0 );
      end
   end

function setBrickAvatar(name)
      if(objects.bricks[name].intHP == 1) then
	 objects.bricks[name].avatar = brick;
      elseif (objects.bricks[name].intHP == 2) then
	 objects.bricks[name].avatar = brick2;
      elseif (objects.bricks[name].intHP == 3) then
	 objects.bricks[name].avatar = brick3;
      elseif (objects.bricks[name].intHP == 4) then
	 objects.bricks[name].avatar = brick4;
      elseif (objects.bricks[name].intHP==5) then
	 objects.bricks[name].avatar = brick5;
      elseif (objects.bricks[name].intHP == 6) then
	 objects.bricks[name].avatar = brick6;
      elseif (objects.bricks[name].intHP == 7) then
	 objects.bricks[name].avatar = brick7;
      elseif (objects.bricks[name].intHP == 8) then
	 objects.bricks[name].avatar = brick8;

      end
end

function healBrickHP(name, dmg)
      objects.bricks[name].intHP =  objects.bricks[name].intHP+dmg
      setBrickAvatar(name)
end

function createBall(name, bx, by, boost)
   objects.balls[name] = {}
   objects.balls[name].body = love.physics.newBody(world, bx, by, 100, 0) 
   objects.balls[name].shape = love.physics.newCircleShape(objects.balls[name].body, 0, 0, 8)
   objects.balls[name].shape:setData(name)
   objects.balls[name].shape:setCategory(5) 
   objects.balls[name].shape:setMask(5, 6)
   objects.balls[name].brickHit = false
   objects.balls[name].wallHit = false
   objects.balls[name].ceilingHit = false
   objects.balls[name].ballHit = false 
   objects.balls[name].isDead = false
   objects.balls[name].markedForDeath = false
   objects.balls[name].isBomb = false
   objects.balls[name].impactX = 0
   objects.balls[name].impactY = 0
   objects.balls[name].intIdleFrames = 0;
   ballNum = ballNum + 1;
   if(boost == true) then
      objects.balls[name].body:setLinearVelocity(0,-480)
   end

end
function createBomb(name, bx, by)
   objects.bombs[name] = {}
   objects.bombs[name].body = love.physics.newBody(world, bx, by, 100, 0) 
   objects.bombs[name].shape = love.physics.newCircleShape(objects.bombs[name].body, 0, 0, 32)
   objects.bombs[name].shape:setData(name)
   objects.bombs[name].shape:setCategory(5) 
   objects.bombs[name].shape:setMask(5, 6)
   objects.bombs[name].brickHit = false
   objects.bombs[name].isDead = false
   objects.bombs[name].markedForDeath = false
   objects.bombs[name].impactX = 0
   objects.bombs[name].impactY = 0
   bombNum = bombNum + 1;
   local sfx =  love.audio.newSource(audioPath.."sfx-01b.mp3", "static")
   playSound(sfx)
   sfx = nil
end

function createBullet(name, bx, by)
   objects.bullets[name] = {}
   objects.bullets[name].body = love.physics.newBody(world, bx, by, 20, 0) 
   objects.bullets[name].shape = love.physics.newCircleShape(objects.bullets[name].body, 0, 0, 8)
   objects.bullets[name].shape:setData(name)
   objects.bullets[name].shape:setCategory(7) 
   objects.bullets[name].shape:setMask(2,4,5,6,7,8,9)
   objects.bullets[name].brickHit = false
   objects.bullets[name].isDead = false
   objects.bullets[name].markedForDeath = false
   objects.bullets[name].body:setLinearVelocity(0,-480)
   bulletNum = bulletNum + 1;
   local sfx =  love.audio.newSource(audioPath.."sfx-09.mp3", "static")
   playSound(sfx)
   sfx = nil
end

function createExplosion(name, ex, ey, ix, iy, strCol)
   xVal = ex
   yVal = ey
   exNum = math.random(5,8)
   if strCol == nil then
      strCol = "red"
   end
   for i = 1, exNum do
      if i > 4 then
         xVal = ex
         yVal = ey + 4
      end
      objects.explosions[name..explosionCount] = {}
      objects.explosions[name..explosionCount].body = love.physics.newBody(world, xVal+ i+4, yVal, math.random(200, 300), i)
      objects.explosions[name..explosionCount].shape = love.physics.newRectangleShape(objects.explosions[name..explosionCount].body, 0, 0, 6, 6, 0) 
      objects.explosions[name..explosionCount].markedForDeath = false;
      objects.explosions[name..explosionCount].shape:setData(name..explosionCount);
      objects.explosions[name..explosionCount].body:applyImpulse( math.random(40), math.random(40), 0, 0 );
      objects.explosions[name..explosionCount].body:setBullet(true)
     
      objects.explosions[name..explosionCount].shape:setCategory(8)
      objects.explosions[name..explosionCount].shape:setMask(2,3,4,5,6)
      if strCol == "red" then
        objects.explosions[name..explosionCount].avatar = pieces[math.random(5)]
      elseif strCol == "orange" then
        objects.explosions[name..explosionCount].avatar = pieces_orange[math.random(5)]
      elseif strCol == "yellow" then
        objects.explosions[name..explosionCount].avatar = pieces_yellow[math.random(5)]
      elseif strCol == "green" then
        objects.explosions[name..explosionCount].avatar = pieces_green[math.random(5)]
      elseif strCol == "blue" then
        objects.explosions[name..explosionCount].avatar = pieces_blue[math.random(5)]
     elseif strCol == "purple" then
        objects.explosions[name..explosionCount].avatar = pieces_purple[math.random(5)]
     elseif strCol == "black" then
        objects.explosions[name..explosionCount].avatar = pieces_black[math.random(5)]
     elseif strCol == "silver" then
        objects.explosions[name..explosionCount].avatar = pieces_silver[math.random(5)]

      end
      
      explosionCount = explosionCount + 1;
         worldUpdate = true
   end

end

function createBonus(bx, by)
   if(bonusDropping == true)then
    --  print ("Pop")
   bonusNum = bonusNum + 1
   xVal = bx
   yVal = by
   rnd = math.random(100)
   if(rnd > 90) then
      name = "BonusM"..bonusNum  
      --rnd = nil
   elseif (rnd <= 20) then
      name = "BonusB"..bonusNum
      -- rnd = nil
   elseif (rnd > 20 and rnd <= 40) then
      name = "BonusS"..bonusNum
      -- rnd = nil
   elseif (rnd > 40 and rnd <= 60) then
      name = "BonusP"..bonusNum
      -- rnd = nil
   elseif (rnd > 60 and rnd <= 75) then
      name = "BonusL"..bonusNum
   elseif (rnd > 75 and rnd <= 95) then
      name = "BonusC"..bonusNum
      -- print(name)
      -- rnd = nil
   end
   objects.bonuses[name] = {}
   objects.bonuses[name].body = love.physics.newBody(world, xVal, yVal, 300, 0)
   objects.bonuses[name].shape = love.physics.newRectangleShape(objects.bonuses[name].body, 0,0,32,16, 0)
   objects.bonuses[name].body:setBullet(true)
   objects.bonuses[name].shape:setMask(3,4,5,6)
   objects.bonuses[name].shape:setCategory(4) 
   objects.bonuses[name].intScore = 500
   objects.bonuses[name].markedForDeath = false
   objects.bonuses[name].shape:setData(name)
  -- print(name)
   bonusDropping = false
 end
end

function activateBonus(strBonus)
   if string.find(strBonus, "BonusP") ~= nil then
      score = score + objects.bonuses[strBonus].intScore
     
   elseif string.find(strBonus, "BonusB") ~= nil then
      createBall("Ball"..ballNum, objects.bonuses[strBonus].body:getX(), objects.paddle.body:getY() - 32, true)
   elseif string.find(strBonus, "BonusS") ~= nil then
      ammo = 20
   elseif string.find(strBonus, "BonusM") ~= nil then
        createBallSplosion()   
   elseif string.find(strBonus, "BonusL") ~= nil then
        intLives = intLives + 1
   elseif string.find(strBonus, "BonusC") ~= nil then
      for i in pairs(objects.balls) do
	 if(objects.balls[i].markedForDeath == false) then
	    objects.balls[i].isBomb = true
	 end
     end
   end
  --killBonus(strBonus)
  killObject(objects.bonuses[strBonus])
  objects.bonuses[strBonus].body:setY(600)	
 playSound(sfx_bonus)
end

function playSound(snd)
   if soundEnabled == true and love.audio.getNumSources() <= maxAudioTracks then
      love.audio.play(snd)
   end
end

function killWorldObjects()
   for i in pairs(objects.explosions) do
       killObject(objects.explosions[i])
   end
   for i in pairs(objects.bonuses) do
       killObject(objects.bonuses[i])
   end
   for i in pairs(objects.balls) do
       killObject(objects.balls[i])
   end
   for i in pairs(objects.bricks) do
       killObject(objects.bricks[i])
   end

end
