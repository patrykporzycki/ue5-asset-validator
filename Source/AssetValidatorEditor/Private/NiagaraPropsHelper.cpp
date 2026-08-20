#include "NiagaraPropsHelper.h"

#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraCommon.h"
#include "NiagaraEffectType.h"

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

        EmitterInfos.Add(Info);
    }

    return EmitterInfos;
}

FString UNiagaraPropsHelper::GetNiagaraEffectTypeName(UNiagaraSystem* System)
{
    if (!System)
    {
        return FString();
    }
    const UNiagaraEffectType* EffectType = System->GetEffectType();
    return EffectType ? EffectType->GetName() : FString();
}

