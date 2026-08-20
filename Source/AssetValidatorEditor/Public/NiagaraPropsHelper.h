#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "NiagaraPropsHelper.generated.h"

USTRUCT(BlueprintType)
struct FNiagaraEmitterBoundsInfo
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly)
	FString EmitterName;

	UPROPERTY(BlueprintReadOnly)
	bool bGpuSim = false;

	UPROPERTY(BlueprintReadOnly)
	bool bLocalSpace = false;

	UPROPERTY(BlueprintReadOnly)
	int32 BoundsMode = 0;

	UPROPERTY(BlueprintReadOnly)
	float EmitterFixedBoundsSize = 0.0f;
};

UCLASS()
class ASSETVALIDATOREDITOR_API UNiagaraPropsHelper : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Niagara Props")
	static TArray<FNiagaraEmitterBoundsInfo> GetNiagaraEmittersData(UNiagaraSystem* System);

	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Niagara Props")
	static FString GetNiagaraEffectTypeName(UNiagaraSystem* System);
};
