mapWidth = 19;
mapHeight= 16;
MAPS={}

function loadMaps()
  for i=1, maxLevel do
    local M={}
    for l in love.filesystem.lines('maps/map.'..i) do
      local R={}
      for c in l:gmatch('.') do
        R[#R+1]=tonumber(c)
      end
      M[#M+1]=R
    end
    MAPS[i]=M
  end
end


function getMap(idx)
  if not MAPS[1] then loadMaps() end
  return MAPS[idx]
end

