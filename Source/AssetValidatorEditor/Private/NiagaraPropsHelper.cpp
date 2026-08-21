#include "NiagaraPropsHelper.h"

#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraCommon.h"
#include "NiagaraLightRendererProperties.h"

TArray<FNiagaraEmitterBoundsInfo> UNiagaraPropsHelper::GetNiagaraEmittersData(UNiagaraSystem* System)
{
    TArray<FNiagaraEmitterBoundsInfo> EmitterInfos;
    if (!System)
    {
        return EmitterInfos;
    }

    const TArray<FNiagaraEmitterHandle>& EmitterHandles = System->GetEmitterHandles();
    for (const FNiagaraEmitterHandle& Handle : EmitterHandles)
    {
        FVersionedNiagaraEmitterData* EmitterData = Handle.GetEmitterData();
        if (!EmitterData)
        {
            continue;
        }

        FNiagaraEmitterBoundsInfo Info;
        Info.EmitterName = Handle.GetName().ToString();
        Info.bGpuSim = EmitterData->SimTarget == ENiagaraSimTarget::GPUComputeSim;
        Info.bLocalSpace = EmitterData->bLocalSpace;
        Info.BoundsMode = static_cast<int32>(EmitterData->CalculateBoundsMode);
        Info.EmitterFixedBoundsSize = EmitterData->FixedBounds.IsValid != 0
            ? EmitterData->FixedBounds.GetSize().GetMax()
            : 0.0f;
        Info.bDeterminism = EmitterData->bDeterminism;
        Info.bEnabled = Handle.GetIsEnabled();
        Info.bFixedBounds = System->bFixedBounds;

        for (const UNiagaraRendererProperties* Renderer : EmitterData->GetRenderers())
        {
            if (Renderer && Renderer->GetIsEnabled())
            {
                Info.NumEnabledRenderers++;
                if (Renderer->IsA<UNiagaraLightRendererProperties>())
                {
                    Info.NumEnabledLightRenderers++;
                }
            }
        }

        EmitterInfos.Add(Info);
    }

    return EmitterInfos;
}


