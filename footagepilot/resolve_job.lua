-- Internal console only. Uses native Resolve APIs; no io, dofile or external bridge.
local function require_ok(value, name) assert(value, 'FootagePilot failed: '..name); return value end
_FP=nil
local ok,err=pcall(function()
  if #(cfg.plates or {})>0 then
    local version=resolve:GetVersion()
    assert(version[1]==21 and version[2]==2,'Screen enum requires recalibration on this Resolve version')
  end
  local pm=resolve:GetProjectManager()
  if cfg.color_preset then
    local version=resolve:GetVersion()
    assert(version[1]==21 and version[2]==2,'Color preset requires calibration on this Resolve version')
  end
  local project=require_ok(pm:CreateProject(cfg.name), 'create fresh project (choose a new job name)')
  _FP={project=project,config=cfg,stage='project'}
  require_ok(project:SetSettings({timelineResolutionWidth=tostring(cfg.width),timelineResolutionHeight=tostring(cfg.height),timelineFrameRate=tostring(cfg.fps)}),'project settings')
  if cfg.color_preset then
    assert(project:GetSetting('colorScienceMode')=='davinciYRGB','Color preset requires DaVinci YRGB')
  end
  local function apply_color(item)
    local look=cfg.color_preset
    if not look then return end
    require_ok(item:SetCDL({NodeIndex='1',Slope='1 1 1',Offset='0 0 0',Power='1 1 1',Saturation=tostring(look.saturation)}),'apply color preset')
    local grade=require_ok(item:GetCDL(1),'read color preset')
    assert(math.abs(tonumber(grade.Saturation)-look.saturation)<0.00001,'Color saturation readback mismatch')
    require_ok(item:GetNodeGraph():SetNodeLabel(1,look.label),'name color node')
    assert(item:GetNodeLabel(1)==look.label,'Color node label readback mismatch')
  end
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
    apply_color(items[1])
  end
  if cfg.music then
    local clips=require_ok(pool:ImportMedia({cfg.music}),'import music')
    local audio=require_ok(pool:AppendToTimeline({{mediaPoolItem=clips[1],startFrame=0,endFrame=cfg.frames,recordFrame=timeline:GetStartFrame(),trackIndex=1,mediaType=2}}),'append music')
    require_ok(audio[1],'music item')
    assert(math.abs(audio[1]:GetDuration()-cfg.frames)<1,'FootagePilot music duration mismatch')
    assert(math.abs(audio[1]:GetStart()-timeline:GetStartFrame())<1,'FootagePilot music start mismatch')
  end
  local function add_layer(row,name)
    require_ok(timeline:AddTrack('video'),name..' track')
    local track=timeline:GetTrackCount('video')
    timeline:SetTrackName('video',track,name)
    local clips=require_ok(pool:ImportMedia({row.path}),name..' import')
    local items=require_ok(pool:AppendToTimeline({{mediaPoolItem=clips[1],startFrame=0,endFrame=row.frames,recordFrame=timeline:GetStartFrame()+row.start,trackIndex=track,mediaType=1}}),name..' append')
    local item=require_ok(items[1],name..' item')
    assert(math.abs(item:GetDuration()-row.frames)<1,name..' duration mismatch')
    assert(math.abs(item:GetStart()-timeline:GetStartFrame()-row.start)<1,name..' start mismatch')
    return item
  end
  for i,row in ipairs(cfg.backgrounds or {}) do add_layer(row,'Layout background '..i) end
  for i,row in ipairs(cfg.overlays or {}) do
    local item=add_layer(row,'Collage '..i)
    require_ok(item:SetProperties({ZoomGang=false}),'independent panel axes')
    require_ok(item:SetProperties({ZoomX=row.width or row.scale,ZoomY=row.height or row.scale,Pan=(row.x-0.5)*cfg.width,Tilt=(0.5-row.y)*cfg.height}),'panel geometry')
    local props=item:GetProperties()
    assert(math.abs(props.ZoomX-(row.width or row.scale))<0.001 and math.abs(props.ZoomY-(row.height or row.scale))<0.001,'Panel native scale readback mismatch')
    apply_color(item)
  end
  for i,row in ipairs(cfg.transitions or {}) do
    local item=add_layer(row,'Transition '..i)
    local c=require_ok(item:AddFusionComp(),'dissolve composition')
    local mi=require_ok(c:FindTool('MediaIn1'),'dissolve media in')
    local mo=require_ok(c:FindTool('MediaOut1'),'dissolve media out')
    local bg=require_ok(c:AddTool('Background'),'transparent background');bg:SetInput('TopLeftAlpha',0)
    local merge=require_ok(c:AddTool('Merge'),'dissolve merge');merge.Background=bg.Output;merge.Foreground=mi.Output
    local start=c:GetAttrs().COMPN_GlobalStart or 0
    local progress='min(max((time-'..start..')/'..(row.frames-1)..',0),1)'
    if row.filter=='transition_wipe_left' then
      local mask=require_ok(c:AddTool('RectangleMask'),'reveal mask')
      mask:SetInput('Height',1.1);mask:SetInput('SoftEdge',0)
      mask.Width:SetExpression(progress)
      mask.Center:SetExpression('Point(('..progress..')/2,0.5)')
      merge.EffectMask=mask.Mask
      require_ok(merge.EffectMask:GetConnectedOutput(),'connected reveal mask')
      merge:SetInput('Blend',1)
    else
      merge.Blend:SetExpression(progress)
    end
    mo.Input=merge.Output
    apply_color(item)
  end
  for i,row in ipairs(cfg.plates or {}) do
    assert(row.blend=='screen','Unsupported motion plate blend')
    local item=add_layer(row,'Screen plate '..i)
    -- Resolve 21.2 calibrated in an isolated project: native Inspector reads Screen.
    require_ok(item:SetProperties({CompositeEnabled=true,CompositeMode=5,Opacity=row.opacity*100}),'Screen composite')
    local props=item:GetProperties()
    assert(props.CompositeEnabled and props.CompositeMode==5 and math.abs(props.Opacity-row.opacity*100)<0.001,'Screen composite readback mismatch')
  end
  for i,row in ipairs(cfg.titles or {}) do
    local item=add_layer(row,'Title '..i)
    local c=require_ok(item:AddFusionComp(),'title composition')
    local mo=require_ok(c:FindTool('MediaOut1'),'title media out')
    local text=require_ok(c:AddTool('TextPlus'),'TextPlus')
    text:SetInput('StyledText',row.text);text:SetInput('Font',row.font or 'Helvetica Neue');text:SetInput('Style',row.bold and 'Bold' or 'Regular')
    -- Logical title units calibrated against actual exports, not an assumed pixel API.
    text:SetInput('Size',row.size/270);text:SetInput('Center',{row.x,1-row.y})
    text:SetInput('Red1',row.color[1]);text:SetInput('Green1',row.color[2]);text:SetInput('Blue1',row.color[3])
    assert(text:GetInput('Font')==(row.font or 'Helvetica Neue'),'Native title font readback mismatch')
    assert(text:GetInput('Style')==(row.bold and 'Bold' or 'Regular'),'Native title weight readback mismatch')
    assert(math.abs(text:GetInput('Size')-row.size/270)<0.00001,'Native title size readback mismatch')
    assert(text:GetInput('StyledText')==row.text,'Native title text readback mismatch')
    mo.Input=text.Output
  end
  assert(math.abs(timeline:GetEndFrame()-timeline:GetStartFrame()-cfg.frames)<1,'FootagePilot timeline extent mismatch')
  for i,frame in ipairs(cfg.beats) do require_ok(timeline:AddMarker(frame,'Blue','Timing '..i,cfg.timing_label or 'Authored timing grid; not a listening verdict',1),'beat marker') end
  require_ok(pm:SaveProject(),'save project')
  require_ok(pm:ExportProject(project:GetName(),cfg.target..'/resolve-project.drp'),'editable project export')
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
