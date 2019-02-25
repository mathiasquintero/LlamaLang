//
//  Array+TokenGenerator.swift
//  Llama
//
//  Created by Mathias Quintero on 24.02.19.
//  Copyright © 2019 Mathias Quintero. All rights reserved.
//

import Foundation

struct EmptyTokenGeneratorError: Error { }

extension Array: TokenGenerator where Element == TokenGenerator {
    
    func take(text: String) throws -> GeneratedToken {
        var lastError: Error = EmptyTokenGeneratorError()
        for generator in self {
            do {
                return try generator.take(text: text)
            } catch {
                lastError = error
            }
        }
        throw lastError
    }
    
}
