using UnrealBuildTool;

public class AssetValidatorEditor : ModuleRules
{
    public AssetValidatorEditor(ReadOnlyTargetRules Target) : base (Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "UnrealEd",
            "ImageCore",
        });
    }

        
}


