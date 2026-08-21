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

	UPROPERTY(BlueprintReadOnly)
	bool bDeterminism = false;

	UPROPERTY(BlueprintReadOnly)
	bool bEnabled = false;

	UPROPERTY(BlueprintReadOnly)
	bool bFixedBounds = false;

	UPROPERTY(BlueprintReadOnly)
	int32 NumEnabledRenderers = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 NumEnabledLightRenderers = 0;
};

UCLASS()
class ASSETVALIDATOREDITOR_API UNiagaraPropsHelper : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Asset Validator|Niagara Props")
	static TArray<FNiagaraEmitterBoundsInfo> GetNiagaraEmittersData(UNiagaraSystem* System);
};
