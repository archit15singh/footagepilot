-- Internal console only. Uses native Resolve APIs; no io, dofile or external bridge.
local function require_ok(value, name) assert(value, 'FootagePilot failed: '..name); return value end
local ok,err=pcall(function()
  local pm=resolve:GetProjectManager()
  local project=require_ok(pm:CreateProject(cfg.name), 'create fresh project (choose a new job name)')
  _FP={project=project,config=cfg,stage='project'}
  require_ok(project:SetSettings({timelineResolutionWidth=tostring(cfg.width),timelineResolutionHeight=tostring(cfg.height),timelineFrameRate=tostring(cfg.fps)}),'project settings')
  local pool=project:GetMediaPool()
  local timeline=require_ok(pool:CreateEmptyTimeline('Reference recreation'), 'timeline')
  require_ok(timeline:SetStartTimecode('00:00:00:00'),'start timecode')
  _FP.timeline=timeline
  for i,shot in ipairs(cfg.shots) do
    local clips=require_ok(pool:ImportMedia({{FilePath=shot.path}}), 'import shot '..i)
    require_ok(clips[1],'imported clip '..i)
    local items=require_ok(pool:AppendToTimeline({{mediaPoolItem=clips[1],startFrame=0,endFrame=shot.frames-1,recordFrame=timeline:GetStartFrame()+shot.start,trackIndex=1,mediaType=1}}),'append shot '..i)
    require_ok(items[1],'appended clip '..i)
    assert(math.abs(items[1]:GetDuration()-shot.frames)<1,'FootagePilot duration mismatch at shot '..i)
    assert(math.abs(items[1]:GetStart()-timeline:GetStartFrame()-shot.start)<1,'FootagePilot cut mismatch at shot '..i)
  end
  if cfg.music then
    local clips=require_ok(pool:ImportMedia({{FilePath=cfg.music}}),'import music')
    require_ok(pool:AppendToTimeline({{mediaPoolItem=clips[1],startFrame=0,endFrame=cfg.frames-1,recordFrame=timeline:GetStartFrame(),trackIndex=1,mediaType=2}}),'append music')
  end
  for i,frame in ipairs(cfg.beats) do require_ok(timeline:AddMarker(frame,'Blue','Timing '..i,'Authored timing grid; not a listening verdict',1),'beat marker') end
  require_ok(pm:SaveProject(),'save project')
  _FP.stage='assembled'
  print('FOOTAGEPILOT_ASSEMBLED',resolve:GetProductName(),resolve:GetVersionString(),timeline:GetEndFrame()-timeline:GetStartFrame(),#cfg.shots,#cfg.beats)
  print('Inspect preview for Media Offline and framing. Render is a separate explicit console command; see docs/resolve/GUIDE.md.')
end)
if not ok then if _FP then _FP.stage='failed';_FP.error=tostring(err) end; print('FOOTAGEPILOT_FAILED',err) end
