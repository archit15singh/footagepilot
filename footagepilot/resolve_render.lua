-- Run only after inspecting the assembled project and native preview.
assert(_FP and _FP.stage=='assembled','No successfully assembled FootagePilot project')
local p=_FP.project
local cfg=_FP.config
assert(resolve:GetProjectManager():GetCurrentProject():GetName()==p:GetName(),'Current project changed')
assert(p:SetCurrentRenderFormatAndCodec('mp4','H264'),'H264 MP4 unavailable in this edition')
assert(p:SetRenderSettings({TargetDir=cfg.target,CustomName=cfg.custom_name,SelectAllFrames=true,ExportVideo=true,ExportAudio=cfg.music~=nil,FormatWidth=cfg.width,FormatHeight=cfg.height,FrameRate=cfg.fps}),'Render settings rejected')
local job=assert(p:AddRenderJob(),'Render job rejected')
_FP.renderJob=job
assert(p:StartRendering({job}),'Native render failed to start')
print('FOOTAGEPILOT_RENDER_STARTED',job)
print('Check status with: for k,v in pairs(_FP.project:GetRenderJobStatus(_FP.renderJob)) do print(k,v) end')
