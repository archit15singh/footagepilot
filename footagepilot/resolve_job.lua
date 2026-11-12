-- Internal console only. Uses native Resolve APIs; no io, dofile or external bridge.
local function require_ok(value, name) assert(value, 'FootagePilot failed: '..name); return value end
_FP=nil
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
    local clips=require_ok(pool:ImportMedia({shot.path}), 'import shot '..i)
    require_ok(clips[1],'imported clip '..i)
    local items=require_ok(pool:AppendToTimeline({clips[1]}),'append shot '..i)
    require_ok(items[1],'appended clip '..i)
    assert(math.abs(items[1]:GetDuration()-shot.frames)<1,'FootagePilot duration mismatch at shot '..i)
    assert(math.abs(items[1]:GetStart()-timeline:GetStartFrame()-shot.start)<1,'FootagePilot cut mismatch at shot '..i)
  end
  if cfg.music then
    local clips=require_ok(pool:ImportMedia({cfg.music}),'import music')
    local audio=require_ok(pool:AppendToTimeline({{mediaPoolItem=clips[1],startFrame=0,endFrame=cfg.frames,recordFrame=timeline:GetStartFrame(),trackIndex=1,mediaType=2}}),'append music')
    require_ok(audio[1],'music item')
    assert(math.abs(audio[1]:GetDuration()-cfg.frames)<1,'FootagePilot music duration mismatch')
    assert(math.abs(audio[1]:GetStart()-timeline:GetStartFrame())<1,'FootagePilot music start mismatch')
  end
  assert(math.abs(timeline:GetEndFrame()-timeline:GetStartFrame()-cfg.frames)<1,'FootagePilot timeline extent mismatch')
  for i,frame in ipairs(cfg.beats) do require_ok(timeline:AddMarker(frame,'Blue','Timing '..i,'Authored timing grid; not a listening verdict',1),'beat marker') end
  require_ok(pm:SaveProject(),'save project')
  _FP.stage='assembled'
  print('FOOTAGEPILOT_ASSEMBLED',resolve:GetProductName(),resolve:GetVersionString(),timeline:GetEndFrame()-timeline:GetStartFrame(),#cfg.shots,#cfg.beats)
  if cfg.render then
    assert(project:SetCurrentRenderMode(1),'Single-clip render unavailable')
    assert(project:SetCurrentRenderFormatAndCodec('mp4','H264'),'H264 MP4 unavailable')
    assert(project:SetRenderSettings({TargetDir=cfg.target,CustomName=cfg.custom_name,SelectAllFrames=true,ExportVideo=true,ExportAudio=cfg.music~=nil,FormatWidth=cfg.width,FormatHeight=cfg.height,FrameRate=cfg.fps}),'Render settings rejected')
    _FP.renderJob=assert(project:AddRenderJob(),'Render job rejected')
    assert(project:StartRendering({_FP.renderJob}),'Native render failed to start')
    resolve:OpenPage('deliver')
    print('FOOTAGEPILOT_RENDER_STARTED',_FP.renderJob)
  else
    print('Inspect native media, then run render.lua. No render requested.')
  end
end)
if not ok then if _FP then _FP.stage='failed';_FP.error=tostring(err); if _FP.timeline then _FP.timeline:SetName('FAILED '..tostring(err):sub(1,100)) end end; print('FOOTAGEPILOT_FAILED',err) end
